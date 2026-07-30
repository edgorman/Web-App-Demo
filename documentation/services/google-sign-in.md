# Google Sign-In

The frontend supports "Sign in with Google" using [Google Identity Services (GSI)](https://developers.google.com/identity/gsi/web/guides/overview). The frontend collects a Google-issued ID token from the user's browser and the backend verifies it before treating the user as authenticated.

## How it works

1. `services/frontend/index.html` loads the GSI client library (`https://accounts.google.com/gsi/client`).
2. `src/hooks/useGoogleAuth.ts` initializes the library with the configured client ID and renders the "Sign in with Google" button (`src/components/common/GoogleSignInButton.tsx`) once the library is ready.
3. On sign-in, Google calls back with a signed JWT credential. The frontend POSTs it to the backend via `src/services/auth.ts` (`POST /api/v1/auth/google`).
4. The backend (`src/service/fastapi/resources/v1/auth.py`) verifies the credential's signature, audience, and issuer using the [`google-auth`](https://google-auth.readthedocs.io/) library, then returns the verified profile (`src/objects/user.py`).
5. The frontend stores the verified profile in `localStorage` so the signed-in state survives a page refresh, and provides a sign-out action that clears it.

The backend never trusts anything from the frontend other than the opaque credential string — the user's identity (id, email, name, picture) always comes from Google's verified token payload, not from client-supplied fields.

## 1. Create an OAuth 2.0 client ID

Follow [Get your Google API client ID](https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid):

1. Open the [Google Cloud Console credentials page](https://console.cloud.google.com/apis/credentials) for the GCP project you want to associate the login with (this can be a separate project from `web-app-demo-dev` / `web-app-demo-prod`).
2. Configure the OAuth consent screen if you haven't already.
3. Click **Create Credentials** > **OAuth client ID**, choose **Web application**.
4. Add each frontend URL that will render the sign-in button under **Authorized JavaScript origins**, e.g.:
   - `http://localhost:3000` for local development
   - the dev frontend Cloud Run URL
   - the prod frontend Cloud Run URL
5. Save and copy the generated **Client ID** (the client secret is not needed — GSI's ID-token flow only uses the client ID).

## 2. Configure the client ID

The same client ID needs to reach three places. Each defaults to an empty string, so the feature deploys safely and simply stays disabled until configured.

| Location | Purpose |
| --- | --- |
| `SERVICE__AUTH__GOOGLE__CLIENT_ID` (backend env var) | Backend verifies tokens are audienced for this client ID. Set via `infrastructure/config/{dev,prod}/terraform.tfvars` -> `google_client_id`, or in `services/backend/.env` for local development. |
| `VITE_GOOGLE_CLIENT_ID` (frontend build-time env var) | Frontend passes this client ID to `google.accounts.id.initialize()`. Set in `services/frontend/.env` for local development. |
| `GOOGLE_CLIENT_ID` (GitHub Actions repository variable) | CI/CD passes this into the frontend Docker build (`docker_build_args` in `push-commit.yaml`). Managed by Terraform via `infrastructure/root/variables.tf` -> `google_client_id` / `infrastructure/root/github_repository.tf`. |

For local development, copy `.env.example` to `.env` in both `services/backend/` and `services/frontend/` and fill in the client ID.

For deployed environments, set `google_client_id` in `infrastructure/config/dev/terraform.tfvars`, `infrastructure/config/prod/terraform.tfvars`, and `infrastructure/root/variables.tf` (or `infrastructure/config/root/terraform.tfvars`), then apply as usual — pushes to `develop`/`main` handle this automatically via CI/CD.

If the client ID is left unset, the frontend shows a "Google sign-in is not configured" message instead of a button, and the backend returns `500` from `/api/v1/auth/google`.
