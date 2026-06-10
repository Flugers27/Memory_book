import uuid

import pytest

from services.Auth.auth_logic import (
    create_access_token,
    create_verification_token,
    revoke_token,
    verify_token,
    verify_verification_token,
)


def test_verification_token_round_trip():
    user_id = uuid.uuid4()
    token = create_verification_token(user_id, expires_minutes=30)

    assert verify_verification_token(token) == user_id


def test_revoke_token_blocks_future_validation():
    user_id = uuid.uuid4()
    token = create_access_token(user_id, "user@example.com")

    revoke_token(token)

    with pytest.raises(Exception):
        verify_token(token, "access")
