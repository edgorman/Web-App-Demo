# Authorization

Authentication answers *who is calling* (see [Google Sign-In](google-sign-in.md)); authorization answers *what that caller may do to a given thing*. The rules live on the thing itself — a **resource** — and are enforced by a FastAPI dependency before any route handler runs, so a handler never has to repeat them.

## Resources

`src/objects/resource.py` defines `Resource`, the base class for anything a request can act on:

- `Resource.Action` is an enum of the actions the resource supports. It is **empty on the base class** — every implementation overrides it with its own actions.
- `Resource.is_user_authorized(user, action)` returns whether a caller may perform an action. It **denies everything by default**, so a resource is only reachable through rules it has explicitly opted into.

The `user` argument is the caller, authenticated or not — either a `User` or Starlette's `UnauthenticatedUser` — so implementations branch on `user.is_authenticated` rather than being called only for signed-in requests.

### The user resource

`src/objects/user.py`'s `User` is the first implementation:

| Action | Who is authorized |
| --- | --- |
| `get_by_id` | Any authenticated user |
| `update_field` | Only the user themselves |
| `delete` | Only the user themselves |

Unauthenticated callers are denied every action.

## The `authorize` dependency

`src/service/fastapi/dependencies/authorize.py` enforces those rules per route, as an ordinary FastAPI dependency rather than middleware:

```python
def authorize(action: Resource.Action, resolver: Callable[..., Optional[Resource]]) -> Callable[..., Resource]:
    def dependency(request: Request, resource: Optional[Resource] = Depends(resolver)) -> Resource:
        ...
    return dependency
```

- `resolver` is itself a dependency — it declares whatever path parameters and dependencies it needs to load the resource (e.g. `resolve_user(user_id: str, user_storage: UserStorage = Depends(get_user_storage))`), the same as any other FastAPI dependency. `authorize` wires it in as `Depends(resolver)`, so FastAPI resolves it after routing, with path parameters already parsed and validated — no manual request-to-route matching needed.
- A route protects itself by depending on `authorize(action, resolver)`'s return value instead of loading the resource directly, e.g. `user: User = Depends(authorize(User.Action.GET_BY_ID, resolve_user))`. The handler receives the already-authorized resource, so it never re-reads it.
- If `resolver` returns `None`, the request is rejected as `404 Not Found` before the handler runs.
- Otherwise `resource.is_user_authorized(request.user, action)` decides: an **unauthenticated** caller who's denied gets `404 Not Found`, so they can't distinguish a resource that exists but denies them from one that doesn't exist at all; an **authenticated** caller who's denied gets `403 Forbidden`, since they're already identified and telling them the resource exists isn't a new leak.

A route with no `authorize(...)` dependency is simply unprotected — `GET /api/v1/hello` stays open, for example.

### Why a dependency instead of middleware

Starlette/FastAPI middleware (`app.add_middleware`) wraps the *entire* app, including the router — it runs before routing, so it has no access to matched path parameters and would need to duplicate route matching itself to find them. FastAPI dependencies run *after* routing, as part of resolving a specific endpoint, so they get path parameters for free and can still raise `HTTPException` to block the request before the handler runs. That makes them the natural fit here, at the cost of declaring authorization per route (via `Depends(...)`) rather than in one central rule list — `resolver` functions are trivial to write and share, so this doesn't add much duplication in practice.

Because dependencies run within the router, ordering against `add_authenticate_middleware` (still real middleware) takes care of itself: middleware always finishes running — setting `request.user` — before any dependency resolution begins, so `authorize` never needs explicit registration-order reasoning the way middleware does. CORS middleware still wraps everything, so a `403`/`404` raised by `authorize` still carries CORS headers.

## Endpoints

`src/service/fastapi/resources/v1/users.py` exposes the user resource under `/api/v1/users/{user_id}`. Each route module defines an `APIRouter` subclass — one per resource — following the shape used by [RecipeDex](https://github.com/edgorman/RecipeDex/blob/develop/backend/internal/service/fastapi/_resources/user.py):

```python
class UserResource(APIRouter):
    def __init__(self, user_storage: UserStorage):
        super().__init__(prefix="/users")
        self.__user_storage = user_storage
        self.add_api_route("/{user_id}", self.get_by_id, methods=["GET"], response_model=Response[GetUserResponse])
        ...

    def get_by_id(self, user: User = Depends(authorize(User.Action.GET_BY_ID, resolve_user))) -> ...:
        ...
```

- **The repository handler is constructed once and passed in.** `FastAPIService.__init__` builds `UserResource(user_storage)` where it mounts the resource — the class never reaches for storage on its own. Route methods that write (`update_field`, `delete`) use `self.__user_storage` directly, ordinary attribute access with no FastAPI machinery involved.
- **Each path is a public method.** `get_by_id`, `update_field`, `delete` are real, individually callable/testable methods, registered in `__init__` via `self.add_api_route(path, self.<method>, methods=[...], response_model=...)` rather than `@router.get(...)` decorators — decorators would run at class-definition time, before an instance (and its storage handler) exists.
- **No `__preprocess`.** Unlike RecipeDex's version, there's no single method combining validation, existence-checking and authorization — that's what `authenticate` (middleware, sets `request.user`) and `authorize` (dependency, checks the resolved resource) already do. Route methods only contain the resource's own business logic.
- **`resolve_user` stays a plain function, not a method.** It's referenced as a parameter default (`Depends(authorize(User.Action.GET_BY_ID, resolve_user))`) on methods defined at class body level, which — like any Python default argument — is evaluated once when the class is defined, before any `UserResource` instance exists. A method resolver (`self.resolve_user`) isn't reachable from there, so `resolve_user` reads storage the same way `_dependencies.get_user_storage` always has: off `app.state`, set once in `FastAPIService.__init__` alongside constructing `UserResource` itself.
- **Explicit request/response schemas per path.** `GetUserResponse`, `UpdateUserRequest`, `UpdateUserResponse` and `DeleteUserResponse` are small `pydantic.BaseModel`s (`ConfigDict(from_attributes=True)` for the response ones, built with `SomeResponse.model_validate(user)`) declared next to the routes that use them, decoupling the API's field-level contract from the `User` domain object — even where today they happen to mirror it 1:1.

| Method | Action | Request | Response |
| --- | --- | --- | --- |
| `GET` | `get_by_id` | — | `GetUserResponse` |
| `PATCH` | `update_field` | `UpdateUserRequest` | `UpdateUserResponse` |
| `DELETE` | `delete` | — | `DeleteUserResponse` |

Because `authorize` returns the resolved resource, route methods take it as a parameter (`user: User = Depends(authorize(...))`) instead of loading it again — one storage read per protected request, not two.

## Adding a resource

1. Add the object under `src/objects/`, subclassing `Resource` and overriding `Action` and `is_user_authorized`.
2. Add a route module under `src/service/fastapi/resources/v1/` defining:
   - request/response schemas for each path;
   - a plain `resolve_<resource>(...)` dependency function that loads it from its path parameter(s), reading any storage via `Depends(get_<resource>_storage)`;
   - a `<Resource>Resource(APIRouter)` class whose `__init__` takes the repository handler(s) it needs, registers each path via `self.add_api_route(...)`, and exposes one public method per path — each depending on `authorize(<Resource>.Action.<ACTION>, resolve_<resource>)` for the ones that need it.
3. In `FastAPIService.__init__`, construct `<Resource>Resource(<handler>)` and `include_router` it where the other resources are mounted.
