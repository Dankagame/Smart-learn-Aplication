import bcrypt
import pytest
from sqlalchemy import select

from app.auth.models import User

REGISTER_URL = "/auth/register"


def make_payload(**overrides):
    payload = {
        "full_name": "Aline Uwase",
        "email": "aline@example.com",
        "password": "StrongPass123",
        "role": "student",
    }
    payload.update(overrides)
    return payload


@pytest.mark.parametrize("role", ["student", "teacher"])
def test_register_with_valid_data_creates_user(client, role):
    response = client.post(REGISTER_URL, json=make_payload(role=role))

    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["full_name"] == "Aline Uwase"
    assert body["email"] == "aline@example.com"
    assert body["role"] == role
    assert "created_at" in body


def test_register_response_never_contains_password(client):
    response = client.post(REGISTER_URL, json=make_payload())

    body = response.json()
    assert "password" not in body
    assert "hashed_password" not in body
    assert "StrongPass123" not in response.text


def test_password_is_stored_as_bcrypt_hash(client, db_session):
    client.post(REGISTER_URL, json=make_payload())

    user = db_session.scalar(select(User).where(User.email == "aline@example.com"))
    assert user.hashed_password != "StrongPass123"
    assert user.hashed_password.startswith("$2b$")
    assert bcrypt.checkpw(b"StrongPass123", user.hashed_password.encode())


def test_duplicate_email_is_rejected(client):
    client.post(REGISTER_URL, json=make_payload())

    response = client.post(REGISTER_URL, json=make_payload(full_name="Another Person"))

    assert response.status_code == 409
    assert response.json()["detail"] == "An account with this email already exists"


def test_duplicate_email_is_case_insensitive(client):
    client.post(REGISTER_URL, json=make_payload())

    response = client.post(REGISTER_URL, json=make_payload(email="ALINE@Example.com"))

    assert response.status_code == 409


def test_password_shorter_than_8_characters_is_rejected(client):
    response = client.post(REGISTER_URL, json=make_payload(password="short7!"))

    assert response.status_code == 422


def test_password_of_exactly_8_characters_is_accepted(client):
    response = client.post(REGISTER_URL, json=make_payload(password="12345678"))

    assert response.status_code == 201


@pytest.mark.parametrize("role", ["admin", "", "Student"])
def test_invalid_role_is_rejected(client, role):
    response = client.post(REGISTER_URL, json=make_payload(role=role))

    assert response.status_code == 422


def test_invalid_email_is_rejected(client):
    response = client.post(REGISTER_URL, json=make_payload(email="not-an-email"))

    assert response.status_code == 422


@pytest.mark.parametrize("missing_field", ["full_name", "email", "password", "role"])
def test_missing_required_field_is_rejected(client, missing_field):
    payload = make_payload()
    del payload[missing_field]

    response = client.post(REGISTER_URL, json=payload)

    assert response.status_code == 422


def test_blank_full_name_is_rejected(client):
    response = client.post(REGISTER_URL, json=make_payload(full_name="   "))

    assert response.status_code == 422
