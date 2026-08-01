"""Test resource base class."""
from starlette.authentication import UnauthenticatedUser
from src.objects.resource import Resource
from src.objects.user import User


class ExampleResource(Resource):
    """Minimal resource implementation used to exercise the base class."""

    class Action(Resource.Action):
        """Actions available on the example resource."""

        READ = "read"


def test_resource_has_no_actions_by_default():
    """Test that the base action enum is empty until an implementation overrides it."""
    assert list(Resource.Action) == []


def test_resource_denies_by_default():
    """Test that the base class denies every action, authenticated or not."""
    resource = ExampleResource()
    user = User(id="123", email="user@example.com", name="Test User")

    assert resource.is_authorized(user, ExampleResource.Action.READ) is False
    assert resource.is_authorized(UnauthenticatedUser(), ExampleResource.Action.READ) is False


def test_resource_implementations_extend_the_action_enum():
    """Test that an implementation's actions are still base resource actions."""
    assert list(ExampleResource.Action) == [ExampleResource.Action.READ]
    assert isinstance(ExampleResource.Action.READ, Resource.Action)


def test_resource_implementations_can_authorize():
    """Test that an implementation can override the default deny."""
    class AlwaysAuthorized(ExampleResource):
        def is_authorized(self, user, action):
            return action == ExampleResource.Action.READ

    assert AlwaysAuthorized().is_authorized(UnauthenticatedUser(), ExampleResource.Action.READ) is True
