from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.auth.models import User
from app.courses.models import Course
from app.courses.service import get_course, get_owned_course
from app.quizzes.models import Choice, Question, Quiz
from app.quizzes.schemas import QuizCreate


class QuizNotFoundError(Exception):
    pass


class NotQuizOwnerError(Exception):
    pass


def quiz_with_questions():
    return (
        select(Quiz)
        .options(joinedload(Quiz.course))
        .options(selectinload(Quiz.questions).selectinload(Question.choices))
    )


def build_questions(data: QuizCreate) -> list[Question]:
    return [
        Question(
            position=position,
            text=question.text,
            explanation=question.explanation,
            choices=[
                Choice(text=option.text, is_correct=option.is_correct)
                for option in question.options
            ],
        )
        for position, question in enumerate(data.questions, start=1)
    ]


def create_quiz(db: Session, course_id: int, teacher: User, data: QuizCreate) -> Quiz:
    course = get_owned_course(db, course_id, teacher)
    quiz = Quiz(
        course=course,
        title=data.title,
        description=data.description,
        questions=build_questions(data),
    )
    db.add(quiz)
    db.commit()
    return get_quiz(db, quiz.id)


def list_course_quizzes(db: Session, course_id: int) -> list[Quiz]:
    course: Course = get_course(db, course_id)
    query = (
        quiz_with_questions()
        .where(Quiz.course_id == course.id)
        .order_by(Quiz.created_at.desc(), Quiz.id.desc())
    )
    return list(db.scalars(query).unique())


def get_quiz(db: Session, quiz_id: int) -> Quiz:
    quiz = db.scalars(quiz_with_questions().where(Quiz.id == quiz_id)).unique().one_or_none()
    if quiz is None:
        raise QuizNotFoundError
    return quiz


def get_owned_quiz(db: Session, quiz_id: int, teacher: User) -> Quiz:
    quiz = get_quiz(db, quiz_id)
    if quiz.course.teacher_id != teacher.id:
        raise NotQuizOwnerError
    return quiz


def delete_quiz(db: Session, quiz: Quiz) -> None:
    db.delete(quiz)
    db.commit()
