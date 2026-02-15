import pytest
from datetime import datetime, timezone, timedelta
from core.security import Security
from infrastructure import User

user_data = User(
    id=1,
    first_name="Test1",
    last_name="Test1",
    email="test1@example.com",
    phone_number="+702321311",
    hashed_password=Security.hash_password("qwerty"),
)


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
            data=user_data,
        )

        assert token is not None

        decoded_token = Security.decode_token(token)

        assert decoded_token["sub"] == "1"
        assert decoded_token["type"] == "access"
        assert "exp" in decoded_token
        assert "iat" in decoded_token
        assert "jti" in decoded_token

        now = datetime.now(timezone.utc).timestamp()
        assert decoded_token["exp"] > now

    def test_create_refresh_token_and_decode(self):
        token = Security.create_refresh_token(
            data=user_data,
            jti="2DA0-JA1L-OS01-962S",
            refresh_exp=datetime.now(timezone.utc) + timedelta(hours=1),
        )

        assert token is not None

        decoded_token = Security.decode_token(token)

        assert decoded_token["sub"] == "1"
        assert decoded_token["type"] == "refresh"

    def test_generate_reset_token_and_hashed(self):
        reset_token = Security.generate_reset_token()

        assert isinstance(reset_token, str)
        assert len(reset_token) > 0

        hashed_reset_token = Security.hash_token_sha256(reset_token)

        assert isinstance(hashed_reset_token, str)
        assert hashed_reset_token == Security.hash_token_sha256(reset_token)

        another_token = Security.generate_reset_token()
        assert Security.hash_token_sha256(another_token) != hashed_reset_token
