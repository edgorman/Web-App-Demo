# User Storage

Authenticated user profiles are persisted to [Firestore](https://cloud.google.com/firestore) (Native mode). There is no dedicated user-management API — storage is wired into the existing authentication middleware, so a user's profile is created on their first sign-in and refreshed on every subsequent one.

## How it works

1. `infrastructure/env/gcp_firestore.tf` provisions one Firestore (Native mode) database per environment, named `<project-id>-database` (e.g. `web-app-demo-dev-database`).
2. `src/storage/user.py` defines `UserStorage`, an abstract interface with `get` / `create` / `update` / `delete`, following the `src/storage/` interface-then-implementation convention documented in the root `CLAUDE.md`.
3. `src/storage/firestore/user.py`'s `FirestoreUserStorage` implements it against a `google.cloud.firestore.Client`, storing each user as a document in a `users` collection keyed by the user's id.
4. `src/cli/cli.py`'s `run` command constructs the Firestore client (from `SERVICE__STORAGE__FIRESTORE__PROJECT_ID` / `SERVICE__STORAGE__FIRESTORE__DATABASE`) and injects `FirestoreUserStorage` into `FastAPIService`, which passes it on to the authentication middleware (`src/service/fastapi/middleware/authenticate.py`).
5. On every successfully-verified request (see [Google Sign-In](google-sign-in.md)), the middleware looks the user up by id: if it's their first sign-in, it creates the record; otherwise it updates it with the latest name/email from the provider token. Either way, the persisted `User` becomes `request.user`.

This mirrors the storage split in [RecipeDex](https://github.com/edgorman/RecipeDex/blob/develop/backend/internal/storage/firestore/user.py) — an abstract interface at the top level of `storage/`, with a concrete Firestore backend beneath it — extended here to actually read and write documents rather than stub the methods out.

## Configuration

| Env var | Purpose |
| --- | --- |
| `SERVICE__STORAGE__FIRESTORE__PROJECT_ID` | GCP project ID for Firestore. Left empty in `terraform.tfvars`-driven deployments — Terraform sets it explicitly per environment (see below); locally, leave it empty to fall back to the project from Application Default Credentials. |
| `SERVICE__STORAGE__FIRESTORE__DATABASE` | Firestore database ID. Deployed environments use `<project-id>-database`, never the literal `(default)` name. Left empty locally, the Firestore client falls back to its own default (`(default)`); local development can instead point at any database you have access to, including the [Firestore emulator](https://firebase.google.com/docs/emulator-suite/connect_firestore). |

### Deployed environments (dev/prod)

`infrastructure/env/gcp_cloud_run.tf` sets both variables on the backend Cloud Run service automatically — `SERVICE__STORAGE__FIRESTORE__PROJECT_ID` from `var.project_id` and `SERVICE__STORAGE__FIRESTORE__DATABASE` from the `google_firestore_database.database` resource — so no manual configuration is needed per environment.

### IAM

The backend's Cloud Run service account (`backend-sa`) is granted `roles/datastore.user` on the project (`infrastructure/env/gcp_service_account.tf`), giving it read/write access to Firestore. This is the only additional IAM role the backend holds beyond running its own Cloud Run service.

### Local development

Copy `.env.example` to `.env` in `services/backend/` and, if needed, fill in `SERVICE__STORAGE__FIRESTORE__PROJECT_ID` / `SERVICE__STORAGE__FIRESTORE__DATABASE`. Running the service locally against real Firestore requires [Application Default Credentials](https://cloud.google.com/docs/authentication/external/set-up-adc) (`gcloud auth application-default login`) with access to the target project; without them, `FirestoreClient` construction fails immediately on startup with `DefaultCredentialsError`.

Tests never touch real Firestore: `tests/conftest.py`'s `user_storage` fixture is a `MagicMock(spec=UserStorage)`, injected via the `user_storage` / `fastapi_service` fixtures.
