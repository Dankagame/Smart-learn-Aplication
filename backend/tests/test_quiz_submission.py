import pytest

RESULTS_URL = "/me/results"

QUIZ_PAYLOAD = {
    "title": "Rwanda Geography",
    "questions": [
        {
            "text": "What is the capital of Rwanda?",
            "explanation": "Kigali has been the capital since independence in 1962.",
            "options": [{"text": "Kigali", "is_correct": True}, {"text": "Huye"}, {"text": "Musanze"}],
        },
        {
            "text": "Which lake lies on Rwanda's western border?",
            "explanation": "Lake Kivu is shared with the DRC.",
            "options": [{"text": "Lake Victoria"}, {"text": "Lake Kivu", "is_correct": True}],
        },
        {
            "text": "How many provinces does Rwanda have, including Kigali?",
            "options": [{"text": "4"}, {"text": "5", "is_correct": True}, {"text": "6"}, {"text": "30"}],
        },
    ],
}


def submit_url(quiz_id: int) -> str:
    return f"/quizzes/{quiz_id}/submit"


@pytest.fixture
def teacher(create_user) -> dict:
    return create_user("teacher", "teacher@example.com", "Jean Habimana")


@pytest.fixture
def student(create_user) -> dict:
    return create_user("student", "student@example.com", "Aline Uwase")


@pytest.fixture
def other_student(create_user) -> dict:
    return create_user("student", "other.student@example.com", "Eric Mugisha")


@pytest.fixture
def course(client, teacher) -> dict:
    response = client.post(
        "/courses",
        json={"title": "Social Studies", "subject": "Geography", "level": "S3"},
        headers=teacher["headers"],
    )
    return response.json()


@pytest.fixture
def answer_key(client, teacher, course) -> dict:
    response = client.post(
        f"/courses/{course['id']}/quizzes", json=QUIZ_PAYLOAD, headers=teacher["headers"]
    )
    assert response.status_code == 201, response.text
    return response.json()


def correct_option(question: dict) -> int:
    return next(option["id"] for option in question["options"] if option["is_correct"])


def wrong_option(question: dict) -> int:
    return next(option["id"] for option in question["options"] if not option["is_correct"])


def answers_for(quiz: dict, pattern: list[bool | None]) -> list[dict]:
    answers = []
    for question, answer_correctly in zip(quiz["questions"], pattern):
        if answer_correctly is None:
            continue
        option_id = correct_option(question) if answer_correctly else wrong_option(question)
        answers.append({"question_id": question["id"], "option_id": option_id})
    return answers


def submit(client, user: dict, quiz: dict, pattern: list[bool | None]):
    return client.post(
        submit_url(quiz["id"]), json={"answers": answers_for(quiz, pattern)}, headers=user["headers"]
    )


class TestScore:
    def test_all_correct_answers_score_100_percent(self, client, student, answer_key):
        response = submit(client, student, answer_key, [True, True, True])

        assert response.status_code == 201
        body = response.json()
        assert body["score"] == 3
        assert body["total"] == 3
        assert body["percentage"] == 100.0

    def test_partial_score_and_rounded_percentage(self, client, student, answer_key):
        body = submit(client, student, answer_key, [True, False, True]).json()

        assert body["score"] == 2
        assert body["total"] == 3
        assert body["percentage"] == 66.7

    def test_all_wrong_answers_score_zero(self, client, student, answer_key):
        body = submit(client, student, answer_key, [False, False, False]).json()

        assert body["score"] == 0
        assert body["percentage"] == 0.0

    def test_unanswered_questions_count_as_wrong(self, client, student, answer_key):
        body = submit(client, student, answer_key, [True, None, None]).json()

        assert body["score"] == 1
        assert body["total"] == 3
        assert body["feedback"][1]["selected_option_id"] is None
        assert body["feedback"][1]["is_correct"] is False

    def test_response_includes_quiz_and_course_details(self, client, student, answer_key, course):
        body = submit(client, student, answer_key, [True, True, True]).json()

        assert body["attempt_id"] > 0
        assert body["quiz_id"] == answer_key["id"]
        assert body["quiz_title"] == "Rwanda Geography"
        assert body["course_id"] == course["id"]
        assert body["course_title"] == "Social Studies"
        assert "submitted_at" in body


class TestFeedback:
    def test_feedback_marks_each_question_right_or_wrong(self, client, student, answer_key):
        body = submit(client, student, answer_key, [True, False, True]).json()

        assert [item["is_correct"] for item in body["feedback"]] == [True, False, True]

    def test_feedback_shows_selected_and_correct_option(self, client, student, answer_key):
        body = submit(client, student, answer_key, [True, False, True]).json()

        wrong = body["feedback"][1]
        question = answer_key["questions"][1]
        assert wrong["question_id"] == question["id"]
        assert wrong["position"] == 2
        assert wrong["question_text"] == question["text"]
        assert wrong["selected_option_id"] == wrong_option(question)
        assert wrong["correct_option_id"] == correct_option(question)
        assert wrong["explanation"] == "Lake Kivu is shared with the DRC."

    def test_feedback_follows_question_order(self, client, student, answer_key):
        body = submit(client, student, answer_key, [True, True, True]).json()

        assert [item["position"] for item in body["feedback"]] == [1, 2, 3]


class TestSubmissionRules:
    def test_teacher_cannot_submit_quiz(self, client, teacher, answer_key):
        response = submit(client, teacher, answer_key, [True, True, True])

        assert response.status_code == 403

    def test_anonymous_user_cannot_submit_quiz(self, client, answer_key):
        response = client.post(submit_url(answer_key["id"]), json={"answers": answers_for(answer_key, [True])})

        assert response.status_code == 401

    def test_unknown_quiz_returns_404(self, client, student):
        response = client.post(
            submit_url(9999), json={"answers": [{"question_id": 1, "option_id": 1}]}, headers=student["headers"]
        )

        assert response.status_code == 404

    def test_empty_submission_is_rejected(self, client, student, answer_key):
        response = client.post(submit_url(answer_key["id"]), json={"answers": []}, headers=student["headers"])

        assert response.status_code == 422

    def test_answering_same_question_twice_is_rejected(self, client, student, answer_key):
        question = answer_key["questions"][0]
        answers = [
            {"question_id": question["id"], "option_id": correct_option(question)},
            {"question_id": question["id"], "option_id": wrong_option(question)},
        ]

        response = client.post(submit_url(answer_key["id"]), json={"answers": answers}, headers=student["headers"])

        assert response.status_code == 422

    def test_question_from_another_quiz_is_rejected(self, client, student, answer_key):
        answers = [{"question_id": 9999, "option_id": correct_option(answer_key["questions"][0])}]

        response = client.post(submit_url(answer_key["id"]), json={"answers": answers}, headers=student["headers"])

        assert response.status_code == 422
        assert response.json()["detail"] == "Question 9999 does not belong to this quiz"

    def test_option_from_another_question_is_rejected(self, client, student, answer_key):
        first, second = answer_key["questions"][0], answer_key["questions"][1]
        answers = [{"question_id": first["id"], "option_id": correct_option(second)}]

        response = client.post(submit_url(answer_key["id"]), json={"answers": answers}, headers=student["headers"])

        assert response.status_code == 422

    def test_rejected_submission_is_not_saved(self, client, student, answer_key):
        answers = [{"question_id": 9999, "option_id": 1}]
        client.post(submit_url(answer_key["id"]), json={"answers": answers}, headers=student["headers"])

        assert client.get(RESULTS_URL, headers=student["headers"]).json() == []

    def test_student_can_retake_quiz(self, client, student, answer_key):
        first = submit(client, student, answer_key, [False, False, False]).json()
        second = submit(client, student, answer_key, [True, True, True]).json()

        assert first["attempt_id"] != second["attempt_id"]
        assert len(client.get(RESULTS_URL, headers=student["headers"]).json()) == 2


class TestMyResults:
    def test_attempt_is_saved_and_listed(self, client, student, answer_key):
        attempt = submit(client, student, answer_key, [True, False, True]).json()

        response = client.get(RESULTS_URL, headers=student["headers"])

        assert response.status_code == 200
        [result] = response.json()
        assert result["attempt_id"] == attempt["attempt_id"]
        assert result["quiz_title"] == "Rwanda Geography"
        assert result["course_title"] == "Social Studies"
        assert (result["score"], result["total"], result["percentage"]) == (2, 3, 66.7)
        assert "feedback" not in result

    def test_results_are_newest_first(self, client, student, answer_key):
        first = submit(client, student, answer_key, [False, False, False]).json()
        second = submit(client, student, answer_key, [True, True, True]).json()

        results = client.get(RESULTS_URL, headers=student["headers"]).json()

        assert [r["attempt_id"] for r in results] == [second["attempt_id"], first["attempt_id"]]

    def test_student_only_sees_own_results(self, client, student, other_student, answer_key):
        submit(client, student, answer_key, [True, True, True])

        assert client.get(RESULTS_URL, headers=other_student["headers"]).json() == []

    def test_student_can_open_past_result_with_feedback(self, client, student, answer_key):
        attempt = submit(client, student, answer_key, [True, False, True]).json()

        response = client.get(f"{RESULTS_URL}/{attempt['attempt_id']}", headers=student["headers"])

        assert response.status_code == 200
        assert response.json() == attempt

    def test_student_cannot_open_another_students_result(self, client, student, other_student, answer_key):
        attempt = submit(client, student, answer_key, [True, True, True]).json()

        response = client.get(f"{RESULTS_URL}/{attempt['attempt_id']}", headers=other_student["headers"])

        assert response.status_code == 404

    def test_results_require_login(self, client):
        assert client.get(RESULTS_URL).status_code == 401

    def test_results_pagination(self, client, student, answer_key):
        for _ in range(3):
            submit(client, student, answer_key, [True, True, True])

        page = client.get(RESULTS_URL, params={"limit": 2}, headers=student["headers"]).json()

        assert len(page) == 2
