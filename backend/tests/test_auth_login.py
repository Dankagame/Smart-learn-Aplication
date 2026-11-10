from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi import APIRouter, Depends

from app.auth.dependencies import require_teacher
from app.auth.models import User
from app.core.config import get_settings
from app.main import app

REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/login"
ME_URL = "/auth/me"
TEACHER_ONLY_URL = "/test-only/teacher-area"

PASSWORD = "StrongPass123"

teacher_only_router = APIRouter()


@teacher_only_router.get(TEACHER_ONLY_URL)
def teacher_area(current_user: User = Depends(require_teacher)) -> dict[str, str]:
    return {"message": f"Welcome, {current_user.full_name}"}


@pytest.fixture(scope="module", autouse=True)
def mount_teacher_only_route():
    app.include_router(teacher_only_router)
    yield
    app.router.routes[:] = [
        route for route in app.router.routes if getattr(route, "path", None) != TEACHER_ONLY_URL
    ]


def register(client, email: str, role: str) -> dict:
    response = client.post(
        REGISTER_URL,
        json={"full_name": "Test User", "email": email, "password": PASSWORD, "role": role},
    )
    assert response.status_code == 201
    return response.json()


def login(client, email: str, password: str = PASSWORD):
    return client.post(LOGIN_URL, json={"email": email, "password": password})


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def make_token(
    subject: str, *, key: str | None = None, expires_in: timedelta = timedelta(minutes=5)
) -> str:
    settings = get_settings()
    issued_at = datetime.now(UTC)
    return jwt.encode(
        {"sub": subject, "iat": issued_at, "exp": issued_at + expires_in},
        key or settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )


@pytest.fixture
def teacher(client) -> dict:
    return register(client, "teacher@example.com", "teacher")


@pytest.fixture
def student(client) -> dict:
    return register(client, "student@example.com", "student")


@pytest.fixture
def teacher_token(client, teacher) -> str:
    return login(client, teacher["email"]).json()["access_token"]


@pytest.fixture
def student_token(client, student) -> str:
    return login(client, student["email"]).json()["access_token"]


class TestLogin:
    def test_correct_credentials_return_jwt_token(self, client, student):
        response = login(client, student["email"])

        assert response.status_code == 200
        body = response.json()
        assert body["token_type"] == "bearer"
        assert body["expires_in"] == get_settings().access_token_expire_minutes * 60
        assert body["user"] == student

    def test_token_identifies_user_and_role(self, client, teacher):
        settings = get_settings()
        token = login(client, teacher["email"]).json()["access_token"]

        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])

        assert payload["sub"] == str(teacher["id"])
        assert payload["role"] == "teacher"
        assert payload["exp"] > payload["iat"]

    def test_email_is_case_insensitive(self, client, student):
        response = login(client, "Student@EXAMPLE.com")

        assert response.status_code == 200

    def test_wrong_password_returns_401(self, client, student):
        response = login(client, student["email"], "WrongPass123")

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"
        assert response.headers["www-authenticate"] == "Bearer"

    def test_unknown_email_returns_same_401_as_wrong_password(self, client, student):
        response = login(client, "nobody@example.com")

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"

    def test_password_longer_than_bcrypt_limit_returns_401(self, client, student):
        response = login(client, student["email"], PASSWORD + "x" * 100)

        assert response.status_code == 401

    def test_response_never_contains_password(self, client, student):
        response = login(client, student["email"])

        assert "hashed_password" not in response.json()["user"]
        assert PASSWORD not in response.text

    @pytest.mark.parametrize(
        "payload",
        [
            {},
            {"email": "student@example.com"},
            {"password": PASSWORD},
            {"email": "not-an-email", "password": PASSWORD},
        ],
    )
    def test_invalid_body_returns_422(self, client, payload):
        response = client.post(LOGIN_URL, json=payload)

        assert response.status_code == 422


class TestProtectedEndpoint:
    def test_valid_token_returns_current_user(self, client, student, student_token):
        response = client.get(ME_URL, headers=bearer(student_token))

        assert response.status_code == 200
        assert response.json() == student

    def test_missing_token_returns_401(self, client):
        response = client.get(ME_URL)

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    @pytest.mark.parametrize(
        "header", ["Bearer", "Bearer not.a.jwt", "Basic dXNlcjpwYXNz", "Token abc"]
    )
    def test_malformed_authorization_header_returns_401(self, client, header):
        response = client.get(ME_URL, headers={"Authorization": header})

        assert response.status_code == 401

    def test_tampered_token_returns_401(self, client, student_token):
        header, payload, signature = student_token.split(".")
        tampered = f"{header}.{payload}.{signature[::-1]}"

        response = client.get(ME_URL, headers=bearer(tampered))

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired token"

    def test_expired_token_returns_401(self, client, student):
        token = make_token(str(student["id"]), expires_in=timedelta(minutes=-1))

        response = client.get(ME_URL, headers=bearer(token))

        assert response.status_code == 401

    def test_token_signed_with_another_key_returns_401(self, client, student):
        token = make_token(str(student["id"]), key="attacker-controlled-secret")

        response = client.get(ME_URL, headers=bearer(token))

        assert response.status_code == 401

    def test_token_with_non_numeric_subject_returns_401(self, client):
        response = client.get(ME_URL, headers=bearer(make_token("abc")))

        assert response.status_code == 401

    def test_token_for_deleted_user_returns_401(self, client, db_session, student, student_token):
        db_session.delete(db_session.get(User, student["id"]))
        db_session.commit()

        response = client.get(ME_URL, headers=bearer(student_token))

        assert response.status_code == 401


class TestRoleBasedAccess:
    def test_teacher_can_access_teacher_only_endpoint(self, client, teacher_token):
        response = client.get(TEACHER_ONLY_URL, headers=bearer(teacher_token))

        assert response.status_code == 200

    def test_student_gets_403_on_teacher_only_endpoint(self, client, student_token):
        response = client.get(TEACHER_ONLY_URL, headers=bearer(student_token))

        assert response.status_code == 403
        assert response.json()["detail"] == "You do not have permission to perform this action"

    def test_teacher_only_endpoint_without_token_returns_401(self, client):
        response = client.get(TEACHER_ONLY_URL)

        assert response.status_code == 401

    def test_role_is_read_from_database_not_token(self, client, db_session, student):
        forged = jwt.encode(
            {
                "sub": str(student["id"]),
                "role": "teacher",
                "iat": datetime.now(UTC),
                "exp": datetime.now(UTC) + timedelta(minutes=5),
            },
            get_settings().secret_key,
            algorithm=get_settings().jwt_algorithm,
        )

        response = client.get(TEACHER_ONLY_URL, headers=bearer(forged))

        assert response.status_code == 403
