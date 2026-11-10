import pytest

COURSES_URL = "/courses"


def course_url(course_id: int) -> str:
    return f"{COURSES_URL}/{course_id}"


def course_payload(**overrides) -> dict:
    payload = {
        "title": "Advanced Mathematics",
        "subject": "Mathematics",
        "level": "S6",
        "description": "Calculus, vectors and past national exam papers.",
    }
    payload.update(overrides)
    return payload


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
    response = client.post(COURSES_URL, json=course_payload(), headers=teacher["headers"])
    assert response.status_code == 201, response.text
    return response.json()


class TestCreateCourse:
    def test_teacher_creates_course(self, client, teacher):
        response = client.post(COURSES_URL, json=course_payload(), headers=teacher["headers"])

        assert response.status_code == 201
        body = response.json()
        assert body["id"] > 0
        assert body["title"] == "Advanced Mathematics"
        assert body["subject"] == "Mathematics"
        assert body["level"] == "S6"
        assert body["teacher_id"] == teacher["id"]
        assert body["teacher_name"] == "Jean Habimana"
        assert "created_at" in body

    def test_owner_comes_from_token_not_request_body(self, client, teacher, other_teacher):
        payload = course_payload(teacher_id=other_teacher["id"], teacher="Someone Else")

        response = client.post(COURSES_URL, json=payload, headers=teacher["headers"])

        assert response.status_code == 201
        assert response.json()["teacher_id"] == teacher["id"]

    def test_input_is_normalized(self, client, teacher):
        payload = course_payload(title="  Organic   Chemistry ", level="s5", description="   ")

        response = client.post(COURSES_URL, json=payload, headers=teacher["headers"])

        body = response.json()
        assert body["title"] == "Organic Chemistry"
        assert body["level"] == "S5"
        assert body["description"] is None

    def test_description_is_optional(self, client, teacher):
        payload = course_payload()
        del payload["description"]

        response = client.post(COURSES_URL, json=payload, headers=teacher["headers"])

        assert response.status_code == 201

    def test_student_cannot_create_course(self, client, student):
        response = client.post(COURSES_URL, json=course_payload(), headers=student["headers"])

        assert response.status_code == 403

    def test_anonymous_user_cannot_create_course(self, client):
        response = client.post(COURSES_URL, json=course_payload())

        assert response.status_code == 401

    @pytest.mark.parametrize(
        "overrides",
        [
            {"title": "AB"},
            {"title": "   "},
            {"subject": "M"},
            {"level": "S7"},
            {"level": "P6"},
            {"level": "Senior 6"},
            {"description": "x" * 2001},
        ],
    )
    def test_invalid_fields_are_rejected(self, client, teacher, overrides):
        response = client.post(
            COURSES_URL, json=course_payload(**overrides), headers=teacher["headers"]
        )

        assert response.status_code == 422

    @pytest.mark.parametrize("missing_field", ["title", "subject", "level"])
    def test_required_fields_are_enforced(self, client, teacher, missing_field):
        payload = course_payload()
        del payload[missing_field]

        response = client.post(COURSES_URL, json=payload, headers=teacher["headers"])

        assert response.status_code == 422


class TestReadCourses:
    def test_logged_in_student_can_view_course(self, client, course, student):
        response = client.get(course_url(course["id"]), headers=student["headers"])

        assert response.status_code == 200
        assert response.json() == course

    def test_unknown_course_returns_404(self, client, student):
        response = client.get(course_url(9999), headers=student["headers"])

        assert response.status_code == 404
        assert response.json()["detail"] == "Course not found"

    def test_listing_requires_login(self, client):
        response = client.get(COURSES_URL)

        assert response.status_code == 401


class TestFilterCourses:
    @pytest.fixture(autouse=True)
    def seeded_courses(self, client, teacher, other_teacher):
        seeds = [
            (teacher, course_payload(title="Calculus", subject="Mathematics", level="S6")),
            (teacher, course_payload(title="Algebra Basics", subject="Mathematics", level="S4")),
            (teacher, course_payload(title="Mechanics", subject="Physics", level="S6")),
            (other_teacher, course_payload(title="Genetics", subject="Biology", level="S5")),
            (other_teacher, course_payload(title="Statistics", subject="Mathematics", level="S6")),
        ]
        for owner, payload in seeds:
            assert (
                client.post(COURSES_URL, json=payload, headers=owner["headers"]).status_code == 201
            )

    def titles(self, client, headers, **params) -> set[str]:
        response = client.get(COURSES_URL, params=params, headers=headers)
        assert response.status_code == 200, response.text
        return {course["title"] for course in response.json()}

    def test_without_filters_returns_all_courses(self, client, student):
        assert len(self.titles(client, student["headers"])) == 5

    def test_filter_by_subject(self, client, student):
        titles = self.titles(client, student["headers"], subject="Mathematics")

        assert titles == {"Calculus", "Algebra Basics", "Statistics"}

    def test_filter_by_level(self, client, student):
        titles = self.titles(client, student["headers"], level="S6")

        assert titles == {"Calculus", "Mechanics", "Statistics"}

    def test_filter_by_subject_and_level(self, client, student):
        titles = self.titles(client, student["headers"], subject="Mathematics", level="S6")

        assert titles == {"Calculus", "Statistics"}

    def test_filters_are_case_insensitive(self, client, student):
        titles = self.titles(client, student["headers"], subject="mathematics", level="s6")

        assert titles == {"Calculus", "Statistics"}

    def test_filter_by_teacher(self, client, student, other_teacher):
        titles = self.titles(client, student["headers"], teacher_id=other_teacher["id"])

        assert titles == {"Genetics", "Statistics"}

    def test_filter_with_no_matches_returns_empty_list(self, client, student):
        assert self.titles(client, student["headers"], subject="History") == set()

    def test_invalid_level_filter_is_rejected(self, client, student):
        response = client.get(COURSES_URL, params={"level": "S9"}, headers=student["headers"])

        assert response.status_code == 422

    def test_pagination(self, client, student):
        first_page = client.get(COURSES_URL, params={"limit": 2}, headers=student["headers"]).json()
        second_page = client.get(
            COURSES_URL, params={"limit": 2, "offset": 2}, headers=student["headers"]
        ).json()

        assert len(first_page) == 2
        assert len(second_page) == 2
        assert {c["id"] for c in first_page}.isdisjoint({c["id"] for c in second_page})


class TestUpdateCourse:
    def test_owner_can_edit_course(self, client, teacher, course):
        response = client.patch(
            course_url(course["id"]),
            json={"title": "Pure Mathematics", "level": "s5"},
            headers=teacher["headers"],
        )

        assert response.status_code == 200
        body = response.json()
        assert body["title"] == "Pure Mathematics"
        assert body["level"] == "S5"
        assert body["subject"] == course["subject"]
        assert body["description"] == course["description"]

    def test_owner_can_clear_description(self, client, teacher, course):
        response = client.patch(
            course_url(course["id"]), json={"description": None}, headers=teacher["headers"]
        )

        assert response.status_code == 200
        assert response.json()["description"] is None

    def test_other_teacher_cannot_edit_course(self, client, other_teacher, teacher, course):
        response = client.patch(
            course_url(course["id"]), json={"title": "Hijacked"}, headers=other_teacher["headers"]
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "You can only modify your own courses"
        unchanged = client.get(course_url(course["id"]), headers=teacher["headers"]).json()
        assert unchanged["title"] == course["title"]

    def test_student_cannot_edit_course(self, client, student, course):
        response = client.patch(
            course_url(course["id"]), json={"title": "Hijacked"}, headers=student["headers"]
        )

        assert response.status_code == 403

    def test_anonymous_user_cannot_edit_course(self, client, course):
        response = client.patch(course_url(course["id"]), json={"title": "Hijacked"})

        assert response.status_code == 401

    def test_editing_unknown_course_returns_404(self, client, teacher):
        response = client.patch(
            course_url(9999), json={"title": "Anything"}, headers=teacher["headers"]
        )

        assert response.status_code == 404

    @pytest.mark.parametrize(
        "payload",
        [
            {},
            {"title": None},
            {"level": "S0"},
            {"teacher_id": 99},
            {"title": "Ok title", "unknown": 1},
        ],
    )
    def test_invalid_update_is_rejected(self, client, teacher, course, payload):
        response = client.patch(course_url(course["id"]), json=payload, headers=teacher["headers"])

        assert response.status_code == 422


class TestDeleteCourse:
    def test_owner_can_delete_course(self, client, teacher, course):
        response = client.delete(course_url(course["id"]), headers=teacher["headers"])

        assert response.status_code == 204
        assert client.get(course_url(course["id"]), headers=teacher["headers"]).status_code == 404

    def test_other_teacher_cannot_delete_course(self, client, other_teacher, teacher, course):
        response = client.delete(course_url(course["id"]), headers=other_teacher["headers"])

        assert response.status_code == 403
        assert client.get(course_url(course["id"]), headers=teacher["headers"]).status_code == 200

    def test_student_cannot_delete_course(self, client, student, course):
        response = client.delete(course_url(course["id"]), headers=student["headers"])

        assert response.status_code == 403

    def test_deleting_unknown_course_returns_404(self, client, teacher):
        response = client.delete(course_url(9999), headers=teacher["headers"])

        assert response.status_code == 404
