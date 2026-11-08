import pytest

from app.quizzes.models import Choice, Question
from app.quizzes.scoring import (
    Grade,
    GradedQuestion,
    QuestionWithoutCorrectOptionError,
    correct_choice,
    grade,
    percentage,
)


def make_question(question_id: int, option_ids: list[int], correct_id: int | None) -> Question:
    return Question(
        id=question_id,
        position=question_id,
        text=f"Question {question_id}",
        choices=[
            Choice(id=option_id, text=f"Option {option_id}", is_correct=option_id == correct_id)
            for option_id in option_ids
        ],
    )


@pytest.fixture
def questions() -> list[Question]:
    return [
        make_question(1, [11, 12, 13], correct_id=11),
        make_question(2, [21, 22], correct_id=22),
        make_question(3, [31, 32, 33, 34], correct_id=33),
    ]


class TestPercentage:
    @pytest.mark.parametrize(
        ("score", "total", "expected"),
        [
            (0, 3, 0.0),
            (1, 3, 33.3),
            (2, 3, 66.7),
            (3, 3, 100.0),
            (1, 2, 50.0),
            (7, 8, 87.5),
            (1, 6, 16.7),
        ],
    )
    def test_percentage_is_rounded_to_one_decimal(self, score, total, expected):
        assert percentage(score, total) == expected

    @pytest.mark.parametrize("total", [0, -1])
    def test_percentage_with_no_questions_is_zero(self, total):
        assert percentage(0, total) == 0.0


class TestCorrectChoice:
    def test_returns_the_correct_option(self):
        question = make_question(1, [11, 12, 13], correct_id=12)

        assert correct_choice(question).id == 12

    def test_question_without_correct_option_raises(self):
        question = make_question(1, [11, 12], correct_id=None)

        with pytest.raises(QuestionWithoutCorrectOptionError):
            correct_choice(question)


class TestGrade:
    def test_all_correct(self, questions):
        result = grade(questions, {1: 11, 2: 22, 3: 33})

        assert (result.score, result.total, result.percentage) == (3, 3, 100.0)
        assert all(question.is_correct for question in result.questions)

    def test_all_wrong(self, questions):
        result = grade(questions, {1: 12, 2: 21, 3: 31})

        assert (result.score, result.total, result.percentage) == (0, 3, 0.0)

    def test_partially_correct(self, questions):
        result = grade(questions, {1: 11, 2: 21, 3: 33})

        assert (result.score, result.total, result.percentage) == (2, 3, 66.7)
        assert [question.is_correct for question in result.questions] == [True, False, True]

    def test_unanswered_question_is_wrong_and_still_counted(self, questions):
        result = grade(questions, {1: 11})

        assert result.score == 1
        assert result.total == 3
        assert result.questions[1].selected_option_id is None
        assert result.questions[1].is_correct is False

    def test_no_answers_scores_zero(self, questions):
        result = grade(questions, {})

        assert (result.score, result.total) == (0, 3)

    def test_feedback_keeps_question_order_and_correct_answers(self, questions):
        result = grade(questions, {2: 21})

        assert [q.question_id for q in result.questions] == [1, 2, 3]
        assert [q.correct_option_id for q in result.questions] == [11, 22, 33]
        assert result.questions[1] == GradedQuestion(
            question_id=2, selected_option_id=21, correct_option_id=22
        )

    def test_answers_for_unknown_questions_are_ignored(self, questions):
        result = grade(questions, {1: 11, 99: 991})

        assert (result.score, result.total) == (1, 3)

    def test_empty_quiz_scores_zero_percent(self):
        result = grade([], {})

        assert result == Grade(questions=())
        assert (result.score, result.total, result.percentage) == (0, 0, 0.0)

    def test_grading_does_not_modify_inputs(self, questions):
        selected = {1: 11, 2: 21}

        grade(questions, selected)

        assert selected == {1: 11, 2: 21}
        assert [c.is_correct for c in questions[0].choices] == [True, False, False]
