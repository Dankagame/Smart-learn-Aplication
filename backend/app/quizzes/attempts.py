from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.auth.models import User
from app.quizzes.models import AttemptAnswer, Question, Quiz, QuizAttempt
from app.quizzes.schemas import QuizSubmission
from app.quizzes.scoring import grade
from app.quizzes.service import get_quiz


class InvalidAnswerError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class AttemptNotFoundError(Exception):
    pass


def attempt_with_details():
    return select(QuizAttempt).options(
        selectinload(QuizAttempt.answers),
        joinedload(QuizAttempt.quiz).options(
            joinedload(Quiz.course),
            selectinload(Quiz.questions).selectinload(Question.choices),
        ),
    )


def validate_answers(quiz: Quiz, submission: QuizSubmission) -> dict[int, int]:
    questions = {question.id: question for question in quiz.questions}
    selected: dict[int, int] = {}
    for answer in submission.answers:
        question = questions.get(answer.question_id)
        if question is None:
            raise InvalidAnswerError(f"Question {answer.question_id} does not belong to this quiz")
        if answer.option_id not in {choice.id for choice in question.choices}:
            raise InvalidAnswerError(
                f"Option {answer.option_id} does not belong to question {answer.question_id}"
            )
        selected[question.id] = answer.option_id
    return selected


def submit_attempt(db: Session, quiz_id: int, student: User, submission: QuizSubmission) -> QuizAttempt:
    quiz = get_quiz(db, quiz_id)
    result = grade(quiz.questions, validate_answers(quiz, submission))

    attempt = QuizAttempt(
        quiz=quiz,
        student=student,
        score=result.score,
        total_questions=result.total,
        answers=[
            AttemptAnswer(
                question_id=graded.question_id,
                choice_id=graded.selected_option_id,
                is_correct=graded.is_correct,
            )
            for graded in result.questions
        ],
    )
    db.add(attempt)
    db.commit()
    return get_student_attempt(db, attempt.id, student)


def get_student_attempt(db: Session, attempt_id: int, student: User) -> QuizAttempt:
    attempt = db.scalars(
        attempt_with_details().where(
            QuizAttempt.id == attempt_id,
            QuizAttempt.student_id == student.id,
        )
    ).unique().one_or_none()
    if attempt is None:
        raise AttemptNotFoundError
    return attempt


def list_student_attempts(
    db: Session, student: User, *, limit: int = 50, offset: int = 0
) -> list[QuizAttempt]:
    query = (
        attempt_with_details()
        .where(QuizAttempt.student_id == student.id)
        .order_by(QuizAttempt.submitted_at.desc(), QuizAttempt.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(query).unique())
