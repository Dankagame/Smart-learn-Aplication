from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, Field, model_validator

from app.quizzes.models import Choice, Quiz

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

