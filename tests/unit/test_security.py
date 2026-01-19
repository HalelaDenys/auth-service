import pytest
from datetime import datetime, timezone
from core.security import Security


class TestSecurity:

    @pytest.mark.parametrize(
        "password, wrong_password",
        [
            ("qwerty", "123456"),
            ("admin_pass", "admin_wrong"),
            ("secret", "notseкcret"),
        ],
    )
    def test_hash_and_verify_password(self, password: str, wrong_password: str) -> None:
        hashed_password = Security.hash_password(password=password)

        assert Security.verify_password(password, hashed_password) is True
        assert Security.verify_password(wrong_password, hashed_password) is False

    def test_create_access_token_and_decode(self):
        token = Security.create_access_token(
            data={"id": 12},
        )

        assert token is not None

        decoded_token = Security.decode_token(token)

        assert decoded_token["sub"] == "12"
        assert decoded_token["type"] == "access"
        assert "exp" in decoded_token
        assert "iat" in decoded_token
        assert "jti" in decoded_token

        now = datetime.now(timezone.utc).timestamp()
        assert decoded_token["exp"] > now
