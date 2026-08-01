"""Authorization middleware checking the resource each request targets."""
from dataclasses import dataclass
from typing import Callable, Iterable, Optional
from fastapi import FastAPI, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Match
from src.objects.resource import Resource


@dataclass(frozen=True)
class AuthorizationRule:
    """Binds an HTTP method and route path to the resource action that request performs.

    Attributes:
        method: HTTP method the rule applies to (e.g. `GET`)
        path: Full route path template the rule applies to (e.g. `/api/v1/users/{user_id}`)
        action: Action the request performs on the resolved resource
        resolver: Loads the resource targeted by the request from the route's path
            parameters, returning None when no such resource exists
    """

    method: str
    path: str
    action: Resource.Action
    resolver: Callable[[dict[str, str]], Optional[Resource]]


class AuthorizeMiddleware(BaseHTTPMiddleware):
    """Rejects requests whose target resource does not authorize the caller.

    Requests that match no rule pass straight through, so a route only becomes
    authorized once a rule is registered for it.
    """

    def __init__(self, app, rules: Iterable[AuthorizationRule]):
        """Initialize the middleware.

        Args:
            app: ASGI application to wrap
            rules: Authorization rules to enforce, keyed internally by method and path
        """
        super().__init__(app)
        self.__rules = {(rule.method.upper(), rule.path): rule for rule in rules}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            self._authorize(request)
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
        return await call_next(request)

    def _authorize(self, request: Request) -> None:
        """Enforce the rule matching this request, if there is one.

        Args:
            request: Incoming request, already resolved to a user by the authentication middleware

        Raises:
            HTTPException: 403 when the resource does not authorize the caller for the action
        """
        rule, path_params = self._get_rule(request)
        if rule is None:
            return

        resource = rule.resolver(path_params)
        if resource is None:
            # Nothing to authorize against — let the route handler report it as not found.
            return

        if not resource.is_authorized(request.user, rule.action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not authorized to perform `{rule.action.value}` on this resource.",
            )

    def _get_rule(self, request: Request) -> tuple[Optional[AuthorizationRule], dict[str, str]]:
        """Find the rule for the route this request resolves to.

        Routing has not run yet at middleware time, so the request is matched against the
        application's routes here to recover the path template and its parameters.

        Args:
            request: Incoming request

        Returns:
            The matching rule (or None) and the route's path parameters
        """
        for route in request.app.routes:
            match, child_scope = route.matches(request.scope)
            if match != Match.FULL:
                continue
            path_params = child_scope.get("path_params", {})
            return self.__rules.get((request.method.upper(), route.path)), path_params

        return None, {}


def add_authorize_middleware(app: FastAPI, rules: Iterable[AuthorizationRule]):
    """Register the authorization middleware.

    Must be registered *before* the authentication middleware: middleware runs in reverse
    registration order, so registering it first means it runs once `request.user` is set.

    Args:
        app: FastAPI application to attach the middleware to
        rules: Authorization rules to enforce
    """
    app.add_middleware(AuthorizeMiddleware, rules=list(rules))
