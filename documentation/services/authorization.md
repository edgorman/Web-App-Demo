# Authorization

Authentication answers *who is calling* (see [Google Sign-In](google-sign-in.md)); authorization answers *what that caller may do to a given thing*. The rules live on the thing itself — a **resource** — and are enforced by middleware before any route handler runs, so a handler never has to repeat them.

## Resources

`src/objects/resource.py` defines `Resource`, the base class for anything a request can act on:

- `Resource.Action` is an enum of the actions the resource supports. It is **empty on the base class** — every implementation overrides it with its own actions.
- `Resource.is_authorized(user, action)` returns whether a caller may perform an action. It **denies everything by default**, so a resource is only reachable through rules it has explicitly opted into.

The `user` argument is the caller, authenticated or not — either a `User` or Starlette's `UnauthenticatedUser` — so implementations branch on `user.is_authenticated` rather than being called only for signed-in requests.

### The user resource

`src/objects/user.py`'s `User` is the first implementation:

| Action | Who is authorized |
| --- | --- |
| `get_by_id` | Any authenticated user |
| `update_field` | Only the user themselves |
| `delete` | Only the user themselves |

Unauthenticated callers are denied every action.

## Middleware

`src/service/fastapi/middleware/authorize.py` enforces those rules per HTTP request:

1. Each protected route is described by an `AuthorizationRule` — an HTTP method, a route path template, the `Resource.Action` that method performs, and a `resolver` that loads the targeted resource from the route's path parameters.
2. On each request the middleware matches the request against the application's routes (routing has not run yet at middleware time) to recover the path template and its parameters, then looks up the rule for that method and path.
3. The resolver loads the resource. If it does not exist, the request continues and the route handler reports it as `404` — the middleware only answers the authorization question.
4. `resource.is_authorized(request.user, action)` decides whether the request continues to the handler. When it returns False: an **unauthenticated** caller gets `404 Not Found`, so they can't distinguish a resource that exists but denies them from one that doesn't exist at all; an **authenticated** caller gets `403 Forbidden`, since they're already identified and telling them the resource exists isn't a new leak.

Requests matching no rule pass straight through — `GET /api/v1/hello` stays open, for example. A route becomes authorized by registering a rule for it, and each resource module builds its own rules (see `users.authorization_rules`), keeping method-to-action mapping next to the routes it describes.

### Middleware ordering

Middleware runs in reverse registration order (last registered is outermost), so `FastAPIService.__init__` registers authorization **before** authentication. The resulting request path is:

```
CORS → authentication (sets request.user) → authorization (checks the resource) → route handler
```

CORS stays outermost so a `403`/`404` from this middleware still carries CORS headers — otherwise a browser would surface the rejection as an opaque CORS error rather than a forbidden/not-found response.

## Endpoints

`src/service/fastapi/resources/v1/users.py` exposes the user resource under `/api/v1/users/{user_id}`:

| Method | Action | Description |
| --- | --- | --- |
| `GET` | `get_by_id` | Fetch a user profile |
| `PATCH` | `update_field` | Update `name` and/or `email`; omitted fields are left unchanged |
| `DELETE` | `delete` | Delete a user profile |

Handlers get their storage backend from `_dependencies.get_user_storage`, which reads the `UserStorage` that `FastAPIService` was constructed with off `app.state` — the same instance the authorization resolvers use (see [User Storage](user-storage.md)).

Because authorization is checked per instance, the middleware loads the targeted resource on every protected request — one storage read before the handler's own. That double read is left as a `TODO` in `authorize.py` (cache the resolved resource on `request.state` and have handlers read it from there) — fine at current scale, worth revisiting if resource lookups get expensive.

## Adding a resource

1. Add the object under `src/objects/`, subclassing `Resource` and overriding `Action` and `is_authorized`.
2. Add the route module under `src/service/fastapi/resources/v1/`, exposing an `APIRouter` plus an `authorization_rules(...)` function returning one `AuthorizationRule` per protected route.
3. In `src/service/fastapi/api.py`, include the router and pass its rules to `add_authorize_middleware`.
