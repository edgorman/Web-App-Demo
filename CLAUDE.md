# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Web-App-Demo is a monorepo with a modular structure for deploying independent features, completely automated via CI/CD:

- `services/backend/` — net/http (Go) API
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
make install   # go mod download
make run       # go run . run  (serves on 127.0.0.1:8080)
make lint      # gofmt -l . (fails if non-empty) && go vet ./...
make format    # gofmt -w .
make test      # go test ./...
```

Run a single test: `go test ./internal/service/nethttp -run TestHelloAnonymous`

Requires Go 1.25+. Config comes from `.env` (copy from `.env.example`), using `SERVICE__` env prefix with `__` as the nested delimiter. Only two third-party modules are used — `cloud.google.com/go/firestore` and `google.golang.org/api/idtoken`; everything else is the standard library, and new code should keep it that way.

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
├── main.go                        # process entry point, calls internal/cli
└── internal/
    ├── cli/                       # flag-based CLI entry point
    ├── config/                    # environment-backed config (one file per concern, e.g. auth.go, storage.go, service.go)
    ├── objects/                   # data models
    ├── service/
    │   ├── api.go                 # API interface
    │   └── nethttp/
    │       ├── api.go             # Service, implements the API interface
    │       ├── middleware/        # e.g. authenticate.go, cors.go
    │       └── resources/v1/      # one handler module per resource
    └── storage/                   # persistence interfaces + backends (e.g. firestore/)
```

- `internal/service/api.go` defines the `API` interface; `internal/service/nethttp/api.go`'s `Service` implements it. Any new HTTP implementation would satisfy the same interface — call sites should depend on the interface, not on `nethttp` directly.
- `internal/config/service.go` builds `ServiceConfig` from `SERVICE__<section>__<field>` env vars (e.g. `SERVICE__HTTP__CORS__ALLOW_ORIGINS`) — double underscores separate nesting levels — seeded from `.env` by `internal/config/env.go`, where process environment variables always win over the file. Binding is explicit per field; list-valued settings are JSON arrays, because that is what Terraform's `jsonencode()` produces. Use `.env.example` as the template for new variables.
- `internal/objects/` holds the data models (e.g. `Message`) — one object per file. Fields persisted to Firestore need explicit `firestore:"..."` tags, or the client writes the Go field names and forks the stored schema.
- `internal/service/nethttp/resources/v1/` holds versioned handler modules, each registered on the v1 `ServeMux` mounted under `/api/v1` in `nethttp.New`. All responses wrap the payload in the generic `Response[T]` type from `resources/v1/objects.go` (adds `timestamp`, `success`, `message`).
- `internal/storage/` holds the persistence layer: an abstract interface at the top level (e.g. `storage/foobar.go`) with concrete backends in subdirectories (e.g. `storage/firestore/foobar.go`), mirroring the `service/api.go` vs `service/nethttp/api.go` split. Storage files manage reading/writing of the object types.
- Tests are co-located `*_test.go` files. Fakes implement the same interfaces the production code depends on; `nethttp.WithTokenVerifier` is the seam that keeps authentication tests off the network.

New backend code should follow this same interface-then-implementation pattern rather than adding logic directly to handlers or the `Service` type. Middleware ordering in `nethttp.New` is load-bearing: CORS wraps authentication so that authentication failures still carry CORS headers and preflights never hit the auth path.

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
- `src/types/models.ts` holds the shared `ApiResponse<T>` type matching the backend's `Response[T]` envelope.
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
- **Access control model**: both Cloud Run services are public at the IAM layer (`allUsers` → `roles/run.invoker`). The frontend is a static SPA that calls the backend directly from the user's browser, so backend requests arrive as anonymous traffic and the `allUsers` binding on the backend is required — without it browsers get a 403 with no CORS headers, which presents as a CORS error. The backend is constrained at the application layer by its CORS allow-list, which Terraform sets via `SERVICE__HTTP__CORS__ALLOW_ORIGINS`. The backend also grants `roles/run.invoker` to the frontend's service account, but that only covers server-side calls, not the browser path. See `documentation/infrastructure/overview.md` and `documentation/services/backend-deployment.md`.
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
