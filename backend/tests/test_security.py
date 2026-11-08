from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.core.config import get_settings
from app.core.security import (
    BCRYPT_MAX_PASSWORD_BYTES,
    InvalidTokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_is_bcrypt_and_not_plain_text(self):
        hashed = hash_password("StrongPass123")

        assert hashed != "StrongPass123"
        assert hashed.startswith("$2b$")

    def test_same_password_gets_different_salt(self):
        assert hash_password("StrongPass123") != hash_password("StrongPass123")

    def test_correct_password_verifies(self):
        assert verify_password("StrongPass123", hash_password("StrongPass123"))

    @pytest.mark.parametrize("attempt", ["WrongPass123", "strongpass123", "StrongPass12", ""])
    def test_wrong_password_does_not_verify(self, attempt):
        assert not verify_password(attempt, hash_password("StrongPass123"))

    def test_password_over_bcrypt_limit_never_verifies(self):
        base = "a" * BCRYPT_MAX_PASSWORD_BYTES
        hashed = hash_password(base)

        assert not verify_password(base + "extra", hashed)

    def test_unicode_password_round_trip(self):
        assert verify_password("Muraho-Rwanda-🇷🇼", hash_password("Muraho-Rwanda-🇷🇼"))


class TestAccessTokens:
    def test_token_round_trip(self):
        token = create_access_token("42", extra_claims={"role": "teacher"})

        payload = decode_access_token(token)

        assert payload["sub"] == "42"
        assert payload["role"] == "teacher"

    def test_token_expires_after_configured_minutes(self):
        settings = get_settings()

        payload = decode_access_token(create_access_token("42"))

        assert payload["exp"] - payload["iat"] == settings.access_token_expire_minutes * 60

    def test_extra_claims_cannot_override_subject_or_expiry(self):
        token = create_access_token("42", extra_claims={"sub": "1", "exp": 9999999999})

        payload = decode_access_token(token)

        assert payload["sub"] == "42"
        assert payload["exp"] < 9999999999

    def test_expired_token_is_rejected(self):
        settings = get_settings()
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        token = jwt.encode(
            {"sub": "42", "iat": past, "exp": past + timedelta(minutes=1)},
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )

        with pytest.raises(InvalidTokenError):
            decode_access_token(token)

    def test_token_signed_with_wrong_key_is_rejected(self):
        now = datetime.now(timezone.utc)
        token = jwt.encode(
            {"sub": "42", "iat": now, "exp": now + timedelta(minutes=5)},
            "wrong-secret",
            algorithm="HS256",
        )

        with pytest.raises(InvalidTokenError):
            decode_access_token(token)

    def test_unsigned_token_is_rejected(self):
        now = datetime.now(timezone.utc)
        token = jwt.encode({"sub": "42", "iat": now, "exp": now + timedelta(minutes=5)}, None, algorithm="none")

        with pytest.raises(InvalidTokenError):
            decode_access_token(token)

    @pytest.mark.parametrize("missing_claim", ["sub", "iat", "exp"])
    def test_token_missing_required_claim_is_rejected(self, missing_claim):
        settings = get_settings()
        now = datetime.now(timezone.utc)
        claims = {"sub": "42", "iat": now, "exp": now + timedelta(minutes=5)}
        del claims[missing_claim]
        token = jwt.encode(claims, settings.secret_key, algorithm=settings.jwt_algorithm)

        with pytest.raises(InvalidTokenError):
            decode_access_token(token)

    @pytest.mark.parametrize("token", ["", "not-a-token", "a.b.c"])
    def test_malformed_token_is_rejected(self, token):
        with pytest.raises(InvalidTokenError):
            decode_access_token(token)
