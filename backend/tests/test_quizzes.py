import copy

import pytest


def quizzes_url(course_id: int) -> str:
    return f"/courses/{course_id}/quizzes"


def quiz_url(quiz_id: int) -> str:
    return f"/quizzes/{quiz_id}"


def answer_key_url(quiz_id: int) -> str:
    return f"/quizzes/{quiz_id}/answer-key"


QUIZ_PAYLOAD = {
    "title": "Derivatives Practice",
    "description": "Senior 6 calculus revision",
    "questions": [
        {
            "text": "What is the derivative of 3x^2 + 4x - 5?",
            "explanation": "Differentiate each term: 6x + 4.",
            "options": [
                {"text": "6x + 4", "is_correct": True},
                {"text": "3x + 4"},
                {"text": "6x^2 + 4"},
                {"text": "6x - 5"},
            ],
        },
        {
            "text": "What is the derivative of a constant?",
            "options": [
                {"text": "0", "is_correct": True},
                {"text": "1"},
            ],
        },
    ],
}


def quiz_payload(**overrides) -> dict:
    payload = copy.deepcopy(QUIZ_PAYLOAD)
    payload.update(overrides)
    return payload


def question_with_options(options: list[dict]) -> dict:
    return {"text": "Pick the right answer", "options": options}


def options(count: int, correct: int | None = 0) -> list[dict]:
    return [{"text": f"Option {i}", "is_correct": i == correct} for i in range(count)]


@pytest.fixture
def teacher(create_user) -> dict:
    return create_user("teacher", "teacher@example.com", "Jean Habimana")


@pytest.fixture
def other_teacher(create_user) -> dict:
    return create_user("teacher", "other.teacher@example.com", "Marie Uwimana")


@pytest.fixture
def student(create_user) -> dict:
    return create_user("student", "student@example.com", "Aline Uwase")


@pytest.fixture
def course(client, teacher) -> dict:
    response = client.post(
        "/courses",
        json={"title": "Advanced Mathematics", "subject": "Mathematics", "level": "S6"},
        headers=teacher["headers"],
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def quiz(client, teacher, course) -> dict:
    response = client.post(quizzes_url(course["id"]), json=quiz_payload(), headers=teacher["headers"])
    assert response.status_code == 201, response.text
    return response.json()


class TestCreateQuiz:
    def test_teacher_creates_quiz_for_own_course(self, client, teacher, course):
        response = client.post(quizzes_url(course["id"]), json=quiz_payload(), headers=teacher["headers"])

        assert response.status_code == 201
        body = response.json()
        assert body["course_id"] == course["id"]
        assert body["title"] == "Derivatives Practice"
        assert body["question_count"] == 2
        first = body["questions"][0]
        assert first["position"] == 1
        assert first["explanation"] == "Differentiate each term: 6x + 4."
        assert [o["text"] for o in first["options"]] == ["6x + 4", "3x + 4", "6x^2 + 4", "6x - 5"]
        assert [o["is_correct"] for o in first["options"]] == [True, False, False, False]

    def test_quiz_with_single_question_is_accepted(self, client, teacher, course):
        payload = quiz_payload(questions=[question_with_options(options(2))])

        response = client.post(quizzes_url(course["id"]), json=payload, headers=teacher["headers"])

        assert response.status_code == 201

    @pytest.mark.parametrize("option_count", [2, 6])
    def test_option_count_boundaries_are_accepted(self, client, teacher, course, option_count):
        payload = quiz_payload(questions=[question_with_options(options(option_count))])

        response = client.post(quizzes_url(course["id"]), json=payload, headers=teacher["headers"])

        assert response.status_code == 201

    def test_student_cannot_create_quiz(self, client, student, course):
        response = client.post(quizzes_url(course["id"]), json=quiz_payload(), headers=student["headers"])

        assert response.status_code == 403

    def test_teacher_cannot_add_quiz_to_another_teachers_course(self, client, other_teacher, course):
        response = client.post(
            quizzes_url(course["id"]), json=quiz_payload(), headers=other_teacher["headers"]
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "You can only add quizzes to your own courses"

    def test_anonymous_user_cannot_create_quiz(self, client, course):
        response = client.post(quizzes_url(course["id"]), json=quiz_payload())

        assert response.status_code == 401

    def test_unknown_course_returns_404(self, client, teacher):
        response = client.post(quizzes_url(9999), json=quiz_payload(), headers=teacher["headers"])

        assert response.status_code == 404


class TestQuizValidation:
    @pytest.mark.parametrize("title", ["", "   ", "AB", "x" * 151])
    def test_invalid_title_is_rejected(self, client, teacher, course, title):
        response = client.post(
            quizzes_url(course["id"]), json=quiz_payload(title=title), headers=teacher["headers"]
        )

        assert response.status_code == 422

    def test_missing_title_is_rejected(self, client, teacher, course):
        payload = quiz_payload()
        del payload["title"]

        response = client.post(quizzes_url(course["id"]), json=payload, headers=teacher["headers"])

        assert response.status_code == 422

    def test_quiz_without_questions_is_rejected(self, client, teacher, course):
        response = client.post(
            quizzes_url(course["id"]), json=quiz_payload(questions=[]), headers=teacher["headers"]
        )

        assert response.status_code == 422

    @pytest.mark.parametrize("option_count", [0, 1, 7])
    def test_option_count_outside_2_to_6_is_rejected(self, client, teacher, course, option_count):
        payload = quiz_payload(questions=[question_with_options(options(option_count))])

        response = client.post(quizzes_url(course["id"]), json=payload, headers=teacher["headers"])

        assert response.status_code == 422

    def test_question_without_correct_answer_is_rejected(self, client, teacher, course):
        payload = quiz_payload(questions=[question_with_options(options(4, correct=None))])

        response = client.post(quizzes_url(course["id"]), json=payload, headers=teacher["headers"])

        assert response.status_code == 422
        assert "exactly one correct option" in response.text

    def test_question_with_two_correct_answers_is_rejected(self, client, teacher, course):
        two_correct = options(4)
        two_correct[1]["is_correct"] = True
        payload = quiz_payload(questions=[question_with_options(two_correct)])

        response = client.post(quizzes_url(course["id"]), json=payload, headers=teacher["headers"])

        assert response.status_code == 422

    def test_duplicate_options_are_rejected(self, client, teacher, course):
        duplicated = [{"text": "Kigali", "is_correct": True}, {"text": " kigali "}]
        payload = quiz_payload(questions=[question_with_options(duplicated)])

        response = client.post(quizzes_url(course["id"]), json=payload, headers=teacher["headers"])

        assert response.status_code == 422

    @pytest.mark.parametrize("text", ["", "  ", "AB"])
    def test_invalid_question_text_is_rejected(self, client, teacher, course, text):
        payload = quiz_payload(questions=[{"text": text, "options": options(2)}])

        response = client.post(quizzes_url(course["id"]), json=payload, headers=teacher["headers"])

        assert response.status_code == 422

    def test_blank_option_text_is_rejected(self, client, teacher, course):
        blank = [{"text": "Correct", "is_correct": True}, {"text": "   "}]
        payload = quiz_payload(questions=[question_with_options(blank)])

        response = client.post(quizzes_url(course["id"]), json=payload, headers=teacher["headers"])

        assert response.status_code == 422

    def test_invalid_quiz_is_not_saved(self, client, teacher, course):
        invalid = quiz_payload(questions=[question_with_options(options(1))])
        client.post(quizzes_url(course["id"]), json=invalid, headers=teacher["headers"])

        listing = client.get(quizzes_url(course["id"]), headers=teacher["headers"])

        assert listing.json() == []


class TestStudentViewHidesAnswers:
    def test_student_sees_questions_and_options(self, client, student, quiz):
        response = client.get(quiz_url(quiz["id"]), headers=student["headers"])

        assert response.status_code == 200
        body = response.json()
        assert body["title"] == quiz["title"]
        assert len(body["questions"]) == 2
        assert [o["text"] for o in body["questions"][0]["options"]] == [
            "6x + 4",
            "3x + 4",
            "6x^2 + 4",
            "6x - 5",
        ]

    def test_correct_answers_are_never_returned_to_students(self, client, student, quiz):
        response = client.get(quiz_url(quiz["id"]), headers=student["headers"])

        assert "is_correct" not in response.text
        assert "explanation" not in response.text
        assert "Differentiate each term" not in response.text
        for question in response.json()["questions"]:
            assert set(question) == {"id", "position", "text", "options"}
            for option in question["options"]:
                assert set(option) == {"id", "text"}

    def test_quiz_list_does_not_include_answers(self, client, student, course, quiz):
        response = client.get(quizzes_url(course["id"]), headers=student["headers"])

        assert response.status_code == 200
        assert response.json()[0]["question_count"] == 2
        assert "is_correct" not in response.text
        assert "questions" not in response.json()[0]

    def test_teacher_also_gets_answer_free_view_on_public_endpoint(self, client, teacher, quiz):
        response = client.get(quiz_url(quiz["id"]), headers=teacher["headers"])

        assert "is_correct" not in response.text

    def test_student_cannot_access_answer_key(self, client, student, quiz):
        response = client.get(answer_key_url(quiz["id"]), headers=student["headers"])

        assert response.status_code == 403
        assert "is_correct" not in response.text

    def test_other_teacher_cannot_access_answer_key(self, client, other_teacher, quiz):
        response = client.get(answer_key_url(quiz["id"]), headers=other_teacher["headers"])

        assert response.status_code == 403
        assert "is_correct" not in response.text

    def test_owner_can_access_answer_key(self, client, teacher, quiz):
        response = client.get(answer_key_url(quiz["id"]), headers=teacher["headers"])

        assert response.status_code == 200
        assert response.json() == quiz

    def test_anonymous_user_cannot_view_quiz(self, client, quiz):
        assert client.get(quiz_url(quiz["id"])).status_code == 401

    def test_unknown_quiz_returns_404(self, client, student):
        assert client.get(quiz_url(9999), headers=student["headers"]).status_code == 404


class TestListAndDeleteQuizzes:
    def test_list_returns_quizzes_for_course(self, client, teacher, student, course, quiz):
        second = client.post(
            quizzes_url(course["id"]),
            json=quiz_payload(title="Integration Practice"),
            headers=teacher["headers"],
        ).json()

        response = client.get(quizzes_url(course["id"]), headers=student["headers"])

        assert [q["id"] for q in response.json()] == [second["id"], quiz["id"]]

    def test_list_for_unknown_course_returns_404(self, client, student):
        assert client.get(quizzes_url(9999), headers=student["headers"]).status_code == 404

    def test_owner_can_delete_quiz(self, client, teacher, quiz):
        response = client.delete(quiz_url(quiz["id"]), headers=teacher["headers"])

        assert response.status_code == 204
        assert client.get(quiz_url(quiz["id"]), headers=teacher["headers"]).status_code == 404

    def test_other_teacher_cannot_delete_quiz(self, client, other_teacher, teacher, quiz):
        response = client.delete(quiz_url(quiz["id"]), headers=other_teacher["headers"])

        assert response.status_code == 403
        assert client.get(quiz_url(quiz["id"]), headers=teacher["headers"]).status_code == 200

    def test_student_cannot_delete_quiz(self, client, student, quiz):
        assert client.delete(quiz_url(quiz["id"]), headers=student["headers"]).status_code == 403

    def test_deleting_course_deletes_its_quizzes(self, client, teacher, course, quiz):
        client.delete(f"/courses/{course['id']}", headers=teacher["headers"])

        assert client.get(quiz_url(quiz["id"]), headers=teacher["headers"]).status_code == 404
