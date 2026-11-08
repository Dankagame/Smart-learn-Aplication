from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from app.quizzes.models import Choice, Question


class QuestionWithoutCorrectOptionError(ValueError):
    pass


@dataclass(frozen=True)
class GradedQuestion:
    question_id: int
    selected_option_id: int | None
    correct_option_id: int

    @property
    def is_correct(self) -> bool:
        return self.selected_option_id == self.correct_option_id


@dataclass(frozen=True)
class Grade:
    questions: tuple[GradedQuestion, ...]

    @property
    def score(self) -> int:
        return sum(question.is_correct for question in self.questions)

    @property
    def total(self) -> int:
        return len(self.questions)

    @property
    def percentage(self) -> float:
        return percentage(self.score, self.total)


def percentage(score: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(score * 100 / total, 1)


def correct_choice(question: Question) -> Choice:
    for choice in question.choices:
        if choice.is_correct:
            return choice
    raise QuestionWithoutCorrectOptionError(f"Question {question.id} has no correct option")


def grade(questions: Sequence[Question], selected_options: Mapping[int, int]) -> Grade:
    return Grade(
        questions=tuple(
            GradedQuestion(
                question_id=question.id,
                selected_option_id=selected_options.get(question.id),
                correct_option_id=correct_choice(question).id,
            )
            for question in questions
        )
    )
