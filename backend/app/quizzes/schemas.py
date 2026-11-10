from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, Field, model_validator

from app.quizzes.models import Choice, Quiz, QuizAttempt
from app.quizzes.scoring import grade, percentage

MIN_OPTIONS = 2
MAX_OPTIONS = 6
MAX_QUESTIONS = 100


def text_with_min_length(min_length: int):
    def validate(value: str) -> str:
        value = " ".join(value.split())
        if len(value) < min_length:
            raise ValueError(f"Must have at least {min_length} characters")
        return value

    return AfterValidator(validate)


def normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


QuizTitle = Annotated[str, Field(max_length=150), text_with_min_length(3)]
QuestionText = Annotated[str, Field(max_length=1000), text_with_min_length(3)]
OptionText = Annotated[str, Field(max_length=500), text_with_min_length(1)]
LongText = Annotated[str | None, Field(max_length=2000), AfterValidator(normalize_optional_text)]


class OptionCreate(BaseModel):
    text: OptionText
    is_correct: bool = False


class QuestionCreate(BaseModel):
    text: QuestionText
    explanation: LongText = None
    options: list[OptionCreate] = Field(min_length=MIN_OPTIONS, max_length=MAX_OPTIONS)

    @model_validator(mode="after")
    def validate_options(self) -> "QuestionCreate":
        correct_count = sum(option.is_correct for option in self.options)
        if correct_count != 1:
            raise ValueError("Each question must have exactly one correct option")
        texts = [option.text.casefold() for option in self.options]
        if len(set(texts)) != len(texts):
            raise ValueError("Options within a question must be unique")
        return self


class QuizCreate(BaseModel):
    title: QuizTitle
    description: LongText = None
    questions: list[QuestionCreate] = Field(min_length=1, max_length=MAX_QUESTIONS)


class OptionPublic(BaseModel):
    id: int
    text: str


class QuestionPublic(BaseModel):
    id: int
    position: int
    text: str
    options: list[OptionPublic]


class QuizSummary(BaseModel):
    id: int
    course_id: int
    title: str
    description: str | None
    question_count: int
    created_at: datetime

    @classmethod
    def from_quiz(cls, quiz: Quiz) -> "QuizSummary":
        return cls(
            id=quiz.id,
            course_id=quiz.course_id,
            title=quiz.title,
            description=quiz.description,
            question_count=len(quiz.questions),
            created_at=quiz.created_at,
        )


class QuizPublic(QuizSummary):
    questions: list[QuestionPublic]

    @classmethod
    def from_quiz(cls, quiz: Quiz) -> "QuizPublic":
        return cls(
            **QuizSummary.from_quiz(quiz).model_dump(),
            questions=[
                QuestionPublic(
                    id=question.id,
                    position=question.position,
                    text=question.text,
                    options=[OptionPublic(id=c.id, text=c.text) for c in ordered(question.choices)],
                )
                for question in quiz.questions
            ],
        )


class OptionWithAnswer(OptionPublic):
    is_correct: bool


class QuestionWithAnswer(BaseModel):
    id: int
    position: int
    text: str
    explanation: str | None
    options: list[OptionWithAnswer]


class QuizWithAnswers(QuizSummary):
    questions: list[QuestionWithAnswer]

    @classmethod
    def from_quiz(cls, quiz: Quiz) -> "QuizWithAnswers":
        return cls(
            **QuizSummary.from_quiz(quiz).model_dump(),
            questions=[
                QuestionWithAnswer(
                    id=question.id,
                    position=question.position,
                    text=question.text,
                    explanation=question.explanation,
                    options=[
                        OptionWithAnswer(id=c.id, text=c.text, is_correct=c.is_correct)
                        for c in ordered(question.choices)
                    ],
                )
                for question in quiz.questions
            ],
        )


def ordered(choices: list[Choice]) -> list[Choice]:
    return sorted(choices, key=lambda choice: choice.id)


class AnswerSubmit(BaseModel):
    question_id: int = Field(gt=0)
    option_id: int = Field(gt=0)


class QuizSubmission(BaseModel):
    answers: list[AnswerSubmit] = Field(min_length=1, max_length=MAX_QUESTIONS)

    @model_validator(mode="after")
    def one_answer_per_question(self) -> "QuizSubmission":
        question_ids = [answer.question_id for answer in self.answers]
        if len(set(question_ids)) != len(question_ids):
            raise ValueError("Each question can only be answered once")
        return self


class QuestionFeedback(BaseModel):
    question_id: int
    position: int
    question_text: str
    selected_option_id: int | None
    correct_option_id: int
    is_correct: bool
    explanation: str | None


class AttemptSummary(BaseModel):
    attempt_id: int
    quiz_id: int
    quiz_title: str
    course_id: int
    course_title: str
    score: int
    total: int
    percentage: float
    submitted_at: datetime

    @classmethod
    def from_attempt(cls, attempt: QuizAttempt) -> "AttemptSummary":
        return cls(
            attempt_id=attempt.id,
            quiz_id=attempt.quiz_id,
            quiz_title=attempt.quiz.title,
            course_id=attempt.quiz.course_id,
            course_title=attempt.quiz.course.title,
            score=attempt.score,
            total=attempt.total_questions,
            percentage=percentage(attempt.score, attempt.total_questions),
            submitted_at=attempt.submitted_at,
        )


class AttemptResult(AttemptSummary):
    feedback: list[QuestionFeedback]

    @classmethod
    def from_attempt(cls, attempt: QuizAttempt) -> "AttemptResult":
        selected = {
            answer.question_id: answer.choice_id
            for answer in attempt.answers
            if answer.choice_id is not None
        }
        questions = attempt.quiz.questions
        graded = grade(questions, selected).questions
        return cls(
            **AttemptSummary.from_attempt(attempt).model_dump(),
            feedback=[
                QuestionFeedback(
                    question_id=question.id,
                    position=question.position,
                    question_text=question.text,
                    selected_option_id=result.selected_option_id,
                    correct_option_id=result.correct_option_id,
                    is_correct=result.is_correct,
                    explanation=question.explanation,
                )
                for question, result in zip(questions, graded, strict=False)
            ],
        )
