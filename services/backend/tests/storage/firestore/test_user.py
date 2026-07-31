"""Test the Firestore-backed user storage."""
from unittest.mock import MagicMock
from src.objects.user import User
from src.storage.firestore.user import FirestoreUserStorage, USERS_COLLECTION


def _client_returning(document_ref: MagicMock) -> MagicMock:
    client = MagicMock()
    client.collection.return_value.document.return_value = document_ref
    return client


def test_get_returns_user_when_document_exists():
    user = User(id="123", email="user@example.com", name="Test User")
    snapshot = MagicMock(exists=True)
    snapshot.to_dict.return_value = user.model_dump()
    document_ref = MagicMock()
    document_ref.get.return_value = snapshot
    client = _client_returning(document_ref)

    result = FirestoreUserStorage(client=client).get("123")

    client.collection.assert_called_once_with(USERS_COLLECTION)
    client.collection.return_value.document.assert_called_once_with("123")
    assert result == user


def test_get_returns_none_when_document_missing():
    snapshot = MagicMock(exists=False)
    document_ref = MagicMock()
    document_ref.get.return_value = snapshot
    client = _client_returning(document_ref)

    assert FirestoreUserStorage(client=client).get("missing") is None


def test_create_writes_user_document():
    user = User(id="123", email="user@example.com", name="Test User")
    document_ref = MagicMock()
    client = _client_returning(document_ref)

    result = FirestoreUserStorage(client=client).create(user)

    document_ref.set.assert_called_once_with(user.model_dump())
    assert result == user


def test_update_merges_user_document():
    user = User(id="123", email="user@example.com", name="Updated Name")
    document_ref = MagicMock()
    client = _client_returning(document_ref)

    result = FirestoreUserStorage(client=client).update(user)

    document_ref.set.assert_called_once_with(user.model_dump(), merge=True)
    assert result == user


def test_delete_removes_user_document():
    document_ref = MagicMock()
    client = _client_returning(document_ref)

    FirestoreUserStorage(client=client).delete("123")

    document_ref.delete.assert_called_once()
