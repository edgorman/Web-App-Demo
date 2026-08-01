"""Test authorization middleware over the user resource."""
import pytest
from src.objects.user import User
from src.service.fastapi.middleware import authenticate as authenticate_middleware

OWNER = User(id="owner-id", email="owner@example.com", name="Owner")
OTHER = User(id="other-id", email="other@example.com", name="Other")


@pytest.fixture(autouse=True)
def stored_users(user_storage):
    """Back the mock storage with a couple of known users."""
    users = {OWNER.id: OWNER, OTHER.id: OTHER}
    user_storage.get.side_effect = lambda user_id: users.get(user_id)
    return users


def authenticate_as(monkeypatch, user: User) -> dict:
    """Make the auth provider resolve every bearer token to `user`, returning its headers."""
    def fake_verify_oauth2_token(credential, request, audience):
        return {"sub": user.id, "email": user.email, "name": user.name}

    monkeypatch.setattr(authenticate_middleware.google_id_token, "verify_oauth2_token", fake_verify_oauth2_token)
    return {"Authorization": "Bearer fake-credential", "Authorization-Provider": "google"}


def test_unauthenticated_caller_gets_not_found(test_client):
    """Test that an unauthenticated caller sees a denied resource as not found, not forbidden.

    This keeps an unauthenticated caller from being able to tell a resource that exists but
    denies them apart from one that doesn't exist at all.
    """
    response = test_client.get(f"/api/v1/users/{OWNER.id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Not found."


def test_authenticated_caller_can_get_another_user(test_client, monkeypatch):
    """Test that any authenticated caller may read a user profile."""
    headers = authenticate_as(monkeypatch, OTHER)

    response = test_client.get(f"/api/v1/users/{OWNER.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["data"] == {"id": OWNER.id, "email": OWNER.email, "name": OWNER.name}


def test_user_can_update_own_fields(test_client, user_storage, monkeypatch):
    """Test that a user may update fields on their own profile."""
    headers = authenticate_as(monkeypatch, OWNER)

    response = test_client.patch(
        f"/api/v1/users/{OWNER.id}", headers=headers, json={"data": {"name": "New Name"}}
    )
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "New Name"
    assert user_storage.update.call_args.args[0] == User(id=OWNER.id, email=OWNER.email, name="New Name")


def test_user_cannot_update_another_users_fields(test_client, user_storage, monkeypatch):
    """Test that a user may not update another user's profile."""
    headers = authenticate_as(monkeypatch, OTHER)

    response = test_client.patch(
        f"/api/v1/users/{OWNER.id}", headers=headers, json={"data": {"name": "New Name"}}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to perform `update_field` on this resource."
    # Sign-in refreshes the caller's own profile, so only the target must be left untouched
    assert all(call.args[0].id != OWNER.id for call in user_storage.update.call_args_list)


def test_user_can_delete_itself(test_client, user_storage, monkeypatch):
    """Test that a user may delete their own profile."""
    headers = authenticate_as(monkeypatch, OWNER)

    response = test_client.delete(f"/api/v1/users/{OWNER.id}", headers=headers)
    assert response.status_code == 200
    user_storage.delete.assert_called_once_with(OWNER.id)


def test_user_cannot_delete_another_user(test_client, user_storage, monkeypatch):
    """Test that a user may not delete another user's profile."""
    headers = authenticate_as(monkeypatch, OTHER)

    response = test_client.delete(f"/api/v1/users/{OWNER.id}", headers=headers)
    assert response.status_code == 403
    user_storage.delete.assert_not_called()


def test_unknown_user_is_not_found(test_client, monkeypatch):
    """Test that a request for a user who does not exist reaches the handler as a 404."""
    headers = authenticate_as(monkeypatch, OWNER)

    response = test_client.get("/api/v1/users/does-not-exist", headers=headers)
    assert response.status_code == 404


def test_unknown_user_is_not_found_when_unauthenticated(test_client):
    """Test that a missing resource is reported as not found rather than forbidden."""
    response = test_client.get("/api/v1/users/does-not-exist")
    assert response.status_code == 404


def test_routes_without_a_rule_are_untouched(test_client):
    """Test that endpoints with no authorization rule stay open."""
    assert test_client.get("/api/v1/hello").status_code == 200


def test_unroutable_requests_are_untouched(test_client):
    """Test that a request matching no route is left to the router to reject."""
    assert test_client.get("/api/v1/not-a-route").status_code == 404


def test_forbidden_response_carries_cors_headers(test_client, monkeypatch):
    """Test that CORS middleware still wraps a rejected request, so browsers see the 403."""
    headers = authenticate_as(monkeypatch, OTHER)
    headers["Origin"] = "https://example.com"

    response = test_client.delete(f"/api/v1/users/{OWNER.id}", headers=headers)
    assert response.status_code == 403
    assert response.headers["access-control-allow-origin"] == "https://example.com"


def test_not_found_response_carries_cors_headers(test_client):
    """Test that CORS middleware still wraps the unauthenticated not-found response."""
    response = test_client.get(f"/api/v1/users/{OWNER.id}", headers={"Origin": "https://example.com"})
    assert response.status_code == 404
    assert response.headers["access-control-allow-origin"] == "https://example.com"
