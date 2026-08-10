# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Web-App-Demo is a monorepo with a modular structure for deploying independent features, completely automated via CI/CD:

- `services/backend/` — FastAPI (Python) API
- `services/frontend/` — React + TypeScript (Vite) SPA
- `infrastructure/` — Terraform for GCP (Cloud Run, Artifact Registry, Workload Identity Federation)

Deployment target: `develop` branch → dev GCP environment, `main` branch → prod GCP environment.

## Branching and release workflow

All changes are made on feature branches and merged via pull request — never commit directly to `develop` or `main`:

1. Branch off `develop` for new work.
2. Open a pull request back into `develop`; merging deploys to the dev GCP environment.
3. Release `develop` to production by opening a pull request from `develop` into `main`; merging deploys to the prod GCP environment.

`develop` is the default base for all new work — always branch off and target `develop`, never `main`. `main` only receives changes via a release PR from `develop` (step 3); it is not a base for feature branches.

## Commands

### Backend (`services/backend/`)

```bash
make install   # uv sync --extra dev
make run       # uv run python -m src.cli.cli run  (serves on 127.0.0.1:8080)
make lint      # uv run flake8 . --exclude .venv --max-line-length 120
make test      # uv run pytest
```

Run a single test: `uv run pytest tests/service/test_fastapi.py::test_name`

Requires Python 3.13+ and `uv`. Config comes from `.env` (copy from `.env.example`), using `SERVICE__` env prefix with `__` as the nested delimiter (pydantic-settings).

### Frontend (`services/frontend/`)

```bash
make install   # npm install
make dev       # npm run dev (localhost:3000)
make build     # tsc && vite build
make lint      # eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0
make format    # prettier --write "src/**/*.{ts,tsx,css}"
```

Backend URL is configured via `VITE_BACKEND_URL` (see `src/config/app.ts`, `.env.example`).

### Infrastructure (`infrastructure/`)

Two independent Terraform roots, each with a `Makefile`:

- `infrastructure/root/` — one-time setup (`make init`) for the admin project: GCS state buckets, Workload Identity Federation, GitHub Actions service account, GitHub repo/variable management.
- `infrastructure/env/` — per-environment (dev/prod) resources: Cloud Run services, Artifact Registry, IAM. Switch environment before running plan/apply:

```bash
cd infrastructure/env
make switch dev   # or: make switch prod   (re-inits backend for that environment)
terraform plan  -var-file=../config/dev/terraform.tfvars
terraform apply -var-file=../config/dev/terraform.tfvars
```

Manual applies are rarely needed — pushes to `develop`/`main` trigger automated `terraform apply` via GitHub Actions.

## Architecture

### Backend: dependency-injection layering

The backend enforces a strict layering convention — preserve this structure when adding files:

```
services/backend/
├── src/
│   ├── cli/                       # click CLI entry point
│   ├── config/                    # pydantic-settings config (one file per concern, e.g. cli.py, storage.py, service.py)
│   ├── objects/                   # pydantic data models
│   ├── service/
│   │   ├── api.py                 # APIServiceInterface (ABC)
│   │   └── fastapi/
│   │       ├── api.py             # FastAPIService, implements APIServiceInterface
│   │       ├── middleware/        # e.g. auth.py, cors.py
│   │       ├── dependencies/      # e.g. authorize.py
│   │       └── resources/v1/      # one router module per resource
│   └── storage/                   # persistence interfaces + backends (e.g. firestore/)
└── tests/                         # mirrors src/ 1:1, plus conftest.py
```

- `src/service/api.py` defines `APIServiceInterface` (ABC); `src/service/fastapi/api.py`'s `FastAPIService` implements it. Any new API framework would implement the same interface — call sites should depend on the interface, not on FastAPI directly.
- `src/config/service.py` uses pydantic-settings (`ServiceConfig`), reading `.env` with `SERVICE__<section>__<field>` env vars (e.g. `SERVICE__FASTAPI__CORS__ALLOW_ORIGINS`) — double underscores separate nesting levels. Use `.env.example` as the template for new variables.
- `src/objects/` holds pydantic data models (e.g. `Message`) — one object per file. Models that requests act on subclass `Resource` (`src/objects/resource.py`), overriding its empty `Action` enum and its deny-by-default `is_user_authorized(user, action)` to declare who may do what (e.g. `User`).
- `src/service/fastapi/dependencies/authorize.py` enforces those rules per route, as a FastAPI dependency rather than middleware: `authorize(action, resolver)` returns a dependency that resolves `resolver` (itself a dependency, e.g. loading a resource from a path parameter), then returns `403`/`404` when the resolved resource does not authorize `request.user`, or the resource otherwise. Routes depend on it directly (`Depends(authorize(...))`) instead of registering centrally — see `documentation/services/authorization.md`.
- `src/service/fastapi/resources/v1/` holds versioned route modules. Each exposes a `<Resource>Resource(APIRouter)` class, constructed with whatever repository handler(s) it needs (e.g. `UserResource(user_storage)`) where `FastAPIService.__init__` mounts it under `/api/v1` — never fetched by the class itself. Routes are built and registered inside `__init__` (not as class-body methods) so a resolver used as a `Depends(authorize(...))` default can close over the constructor's handler(s) directly; each is still assigned to `self` as a public, individually callable method (e.g. `self.get_by_id`, `self.update_field`) before being registered via `self.add_api_route(path, self.<method>, ...)`. Each path has an explicit request/response `pydantic.BaseModel` rather than reusing the domain object directly. All responses wrap the payload in the generic `Response[DataT]` model from `resources/v1/_objects.py` (adds `timestamp`, `success`, `message`).
- `src/storage/` is reserved for a future persistence layer: an abstract interface at the top level (e.g. `storage/foobar.py`) with concrete backends in subdirectories (e.g. `storage/firestore/foobar.py`), mirroring the `service/api.py` vs `service/fastapi/api.py` split. Storage files manage reading/writing of the pydantic object classes.
- `tests/` mirrors `src/` 1:1; shared fixtures (`service_config`, `fastapi_service`, `test_client`) live in `tests/conftest.py`.

New backend code should follow this same interface-then-implementation pattern rather than adding logic directly to route handlers or the FastAPI class.

### Frontend: conventional Vite/React structure

Target structure — not all of it exists yet, but new code should be placed accordingly rather than added ad hoc to `App.tsx`:

```
services/frontend/
├── src/
│   ├── components/
│   │   ├── common/      # reusable UI (buttons, inputs, cards)
│   │   ├── layout/      # headers, footers, sidebars
│   │   └── pages/       # page-level components composing smaller ones
│   ├── hooks/           # custom React hooks for reusable logic
│   ├── services/        # API clients (e.g. api.ts)
│   ├── types/           # shared TypeScript types
│   ├── utils/           # helper functions
│   ├── config/          # app config (API endpoints, feature flags)
│   ├── App.tsx
│   └── main.tsx
└── tests/                # mirrors src/, plus setup.ts
```

- `src/services/api.ts` (`fetchFromBackend`) is the sole fetch wrapper — it builds URLs from `config.backendUrl` (`src/config/app.ts`, driven by `VITE_BACKEND_URL`) and normalizes errors (HTTP-status, JSON-parse, and network-error cases). New backend calls should go through this wrapper rather than calling `fetch` directly.
- `src/types/models.ts` holds the shared `ApiResponse<T>` type matching the backend's `Response[DataT]` envelope.
- Prefer functional components with hooks; mock API calls in component/hook tests rather than hitting the network.

### Infrastructure: root vs. env split

Two Terraform folders, each independently applied:

```
infrastructure/
├── config/{dev,prod,root}/   # terraform.tfvars + terraform.tfbackend per environment
├── env/                      # per-environment resources (Makefile, providers.tf, variables.tf, ...)
└── root/                     # admin/root project (Makefile, providers.tf, variables.tf, ...)
```

- **Root project** (`web-app-demo-root`): Terraform state buckets for all projects, Workload Identity Federation, the GitHub Actions service account, and GitHub repo/variable management. Project-level IAM grants to environment projects (`roles/admin`) are defined here, not in `env/`.
- **Environment projects** (`web-app-demo-dev`, `web-app-demo-prod`): Cloud Run services, Artifact Registry, per-service custom service accounts and IAM. `infrastructure/config/{dev,prod,root}/` holds the corresponding `terraform.tfvars`/`terraform.tfbackend`.
- **Access control model**: both Cloud Run services are public at the IAM layer (`allUsers` → `roles/run.invoker`). The frontend is a static SPA that calls the backend directly from the user's browser, so backend requests arrive as anonymous traffic and the `allUsers` binding on the backend is required — without it browsers get a 403 with no CORS headers, which presents as a CORS error. The backend is constrained at the application layer by the FastAPI CORS allow-list, which Terraform sets via `SERVICE__FASTAPI__CORS__ALLOW_ORIGINS`. The backend also grants `roles/run.invoker` to the frontend's service account, but that only covers server-side calls, not the browser path. See `documentation/infrastructure/overview.md` and `documentation/services/backend-deployment.md`.
- Authentication throughout CI/CD is via Workload Identity Federation (OIDC) — no long-lived GCP service account keys.
- Use Terraform modules for reusable patterns, always remote state (GCS), least-privilege IAM, and tag GCP resources for cost tracking. Document infrastructure changes in `documentation/infrastructure/`. Test in dev before prod.

### CI/CD

```
.github/
├── workflows/
│   ├── pull-request.yaml   # PRs to main/develop: dynamic diffing, terraform plan/validate, service lint/test/build, PR comments
│   └── push-commit.yaml    # merges to main/develop: terraform apply, service build+deploy
└── actions/                 # composite actions shared across workflows (e.g. github-file-diff using dorny/paths-filter)
```

- Dynamic path-diffing (`github-file-diff` composite action, backed by `dorny/paths-filter`) determines which of infrastructure (root/dev/prod) or services (backend/frontend) changed, and only the relevant validate/plan (PR) or apply/deploy (push) jobs run.
- Backend and frontend each build/push a Docker image (tagged with both commit SHA and `latest`) to Artifact Registry and update the corresponding Cloud Run service on merge; `dev` deploys from `develop`, `prod` deploys from `main`.
- Workflows use minimal permissions (`contents: read`, `id-token: write`, `pull-requests: write` where needed for PR comments), extract common steps into composite actions, and use `needs`/`always()` for cross-job conditionals (e.g. env plans waiting on root when root files change in the same PR).
- Full details in `documentation/cicd/overview.md`.
