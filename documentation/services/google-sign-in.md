# Google Sign-In

The frontend supports "Sign in with Google" using [Google Identity Services (GSI)](https://developers.google.com/identity/gsi/web/guides/overview). Authentication is enforced by backend middleware — there is no dedicated login endpoint. The frontend sends the Google-issued ID token as a bearer credential on each request, and the backend verifies it per-request.

## How it works

1. `services/frontend/index.html` loads the GSI client library (`https://accounts.google.com/gsi/client`).
2. `src/hooks/useGoogleAuth.ts` initializes the library with the configured client ID and renders the "Sign in with Google" button (`src/components/common/GoogleSignInButton.tsx`) once the library is ready.
3. On sign-in, Google calls back with a signed JWT credential. The frontend decodes it client-side (for display only — `id`/`email`/`name`) and holds onto the raw credential as the bearer token for the session; there is no backend call at sign-in time.
4. On every backend request, the frontend attaches `Authorization: Bearer <credential>` and `Authorization-Provider: google` headers (`src/hooks/useGoogleAuth.ts`'s `authHeaders`).
5. The backend's authentication middleware (`src/service/fastapi/middleware/authenticate.py`, registered on every request via `AuthenticationMiddleware`) verifies the credential's signature, audience, and issuer using the [`google-auth`](https://google-auth.readthedocs.io/) library, and attaches the verified profile to `request.user` (`src/objects/user.py`). Route handlers — e.g. `GET /api/v1/hello` (`src/service/fastapi/resources/v1/hello.py`) — read `request.user` to personalize behavior, but authentication itself isn't tied to any specific route.
6. Requests with no `Authorization` header are treated as anonymous (`request.user.is_authenticated` is `False`), not rejected — routes opt into requiring authentication themselves (none currently do).

The backend never trusts anything from the frontend other than the opaque credential string — the user's identity (id, email, name) always comes from Google's verified token payload, not from client-supplied fields. Because there's no server-side session, signing out is purely client-side (`useGoogleAuth`'s `signOut`, which clears local state and calls `google.accounts.id.disableAutoSelect()`) and a page refresh clears the signed-in state — the user signs in again via the GSI button.

This mirrors the middleware-based approach in [RecipeDex](https://github.com/edgorman/RecipeDex/blob/develop/backend/internal/service/fastapi/middleware/authenticate.py), generalized to a `google` auth provider (RecipeDex uses `firebase`) via the same `Authorization` / `Authorization-Provider` header convention and provider-dispatch pattern, so adding another provider later is a matter of extending `AuthProvider` and the `match` in `AuthenticateBackend.authenticate`, not restructuring the auth flow.

## 1. Create an OAuth 2.0 client ID

Follow [Get your Google API client ID](https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid):

1. Open the [Google Cloud Console credentials page](https://console.cloud.google.com/apis/credentials) for the `web-app-demo-root` GCP project — since the client ID is defined once in `infrastructure/root` and reused by every environment (see below), it should be created there too, not in `web-app-demo-dev` / `web-app-demo-prod`.
2. Configure the OAuth consent screen if you haven't already.
3. Click **Create Credentials** > **OAuth client ID**, choose **Web application**.
4. Add each frontend URL that will render the sign-in button under **Authorized JavaScript origins**, e.g.:
   - `http://localhost:3000` for local development
   - the dev frontend Cloud Run URL
   - the prod frontend Cloud Run URL
5. Leave **Authorized redirect URIs** empty — it doesn't apply here. That field is for OAuth 2.0 authorization-code/redirect flows; GSI's ID-token flow (`google.accounts.id`, what this app uses) returns the credential straight to the page's JS callback via a popup/One Tap, with no server-side redirect involved.
6. Save and copy the generated **Client ID** (the client secret is not needed — GSI's ID-token flow only uses the client ID).

## 2. Configure the client ID

A single OAuth client ID (with authorized origins for both dev and prod) is defined **once**, in the root project, and reused everywhere — it isn't duplicated per environment.

### Deployed environments (dev/prod)

1. Set `google_client_id` in `infrastructure/root/variables.tf` (or `infrastructure/config/root/terraform.tfvars`) and apply `infrastructure/root` — this is a one-time, root-only Terraform apply that also runs automatically on merges to `main`.
2. That apply writes the value into a `GOOGLE_CLIENT_ID` GitHub Actions repository variable (`infrastructure/root/github_repository.tf`).
3. From there, CI wires it into both dev and prod automatically, with no further per-environment configuration:
   - `push-commit.yaml`/`pull-request.yaml` pass it to `terraform plan`/`apply` for `infrastructure/env` as `TF_VAR_google_client_id`, which becomes the backend Cloud Run service's `SERVICE__AUTH__GOOGLE__CLIENT_ID` env var (`infrastructure/env/gcp_cloud_run.tf`) for both `web-app-demo-dev` and `web-app-demo-prod`.
   - `push-commit.yaml` passes it to the frontend Docker build as `VITE_GOOGLE_CLIENT_ID` (`docker_build_args`), for both dev and prod frontend images.

`infrastructure/env`'s `google_client_id` variable still exists (it's what the Cloud Run env var is set from) but is intentionally left out of `infrastructure/config/dev/terraform.tfvars` and `infrastructure/config/prod/terraform.tfvars` — it's supplied by CI, not per-environment tfvars.

### Local development

Copy `.env.example` to `.env` in both `services/backend/` and `services/frontend/` and fill in `SERVICE__AUTH__GOOGLE__CLIENT_ID` / `VITE_GOOGLE_CLIENT_ID` with the same client ID (make sure `http://localhost:3000` is one of its authorized JavaScript origins).

If the client ID is left unset, the frontend shows a "Google sign-in is not configured" message instead of a button, and any authenticated request (one carrying `Authorization`/`Authorization-Provider` headers) gets a `500` from the middleware.
