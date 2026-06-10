import uuid

from services.Acces_Memory.crud import can_manage_access, normalize_uuid


def test_normalize_uuid_accepts_string_and_uuid_object():
    user_id = uuid.uuid4()

    assert normalize_uuid(str(user_id)) == user_id
    assert normalize_uuid(user_id) == user_id


def test_can_manage_access_allows_owner_or_grantor():
    page_owner_id = uuid.uuid4()
    grantor_id = uuid.uuid4()
    other_user_id = uuid.uuid4()

    assert can_manage_access(page_owner_id, page_owner_id, grantor_id)
    assert can_manage_access(page_owner_id, grantor_id, grantor_id)
    assert not can_manage_access(page_owner_id, other_user_id, grantor_id)
