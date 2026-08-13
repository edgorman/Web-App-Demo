# Backend Service

A Go backend service for Web-App-Demo with a clean architecture following dependency injection principles.

## Architecture

The backend follows a structured architecture with clear separation of concerns:

```
services/backend/
├── main.go               # Process entry point
├── internal/
│   ├── cli/              # Command-line interface
│   ├── config/           # Configuration from the environment and .env
│   ├── objects/          # Data models
│   ├── service/          # Service layer with API interface
│   │   └── nethttp/      # net/http implementation
│   │       ├── middleware/    # e.g. authenticate.go, cors.go
│   │       └── resources/v1/  # API endpoints grouped by version
│   └── storage/          # Storage layer (interface + Firestore backend)
└── .env.example          # Environment variable template
```

Tests live beside the code they cover as `*_test.go`, following Go convention.

### Key Design Principles

- **Dependency Injection**: Components are loosely coupled through interfaces
- **Standard library first**: `net/http`, `encoding/json` and `flag` do the work; the only
  third-party dependencies are the Google client libraries for Firestore and ID token verification
- **Configuration**: Environment variables under the `SERVICE__` prefix, with `.env` file support
- **Testability**: Interfaces are faked in tests; token verification is injectable so no test
  reaches the network

## Prerequisites

- Go 1.25 or higher
- Docker (optional, for containerized deployment)

## Setup

Install dependencies:

```bash
make install
```

Or using go directly:

```bash
go mod download
```

## Running the Service

### Local Development

Start the development server:

```bash
make run
```

Or using the CLI:

```bash
go run . run
```

The service will be available at `http://127.0.0.1:8080`

### Docker

Build the Docker image:

```bash
docker build -t web-app-demo-backend .
```

Run the container:

```bash
docker run -d -p 8080:8080 --name backend web-app-demo-backend
```

The service will be available at `http://localhost:8080`

Stop the container:

```bash
docker stop backend
docker rm backend
```

## Development

### Linting

Run code linting (`gofmt` check plus `go vet`):

```bash
make lint
```

Reformat the code in place:

```bash
make format
```

### Testing

Run tests:

```bash
make test
```

Run a single test: `go test ./internal/service/nethttp -run TestHelloAnonymous`

## API Endpoints

- `GET /api/v1/hello` - Returns a welcome message, personalized if the caller is authenticated

## Authentication

Authentication is enforced by middleware (`internal/service/nethttp/middleware/authenticate.go`), not a dedicated endpoint: requests carrying `Authorization: Bearer <token>` and `Authorization-Provider: google` headers are verified per-request and resolved to a `User` on the request context; requests without those headers are treated as anonymous. See [Google Sign-In](../../documentation/services/google-sign-in.md).

## Configuration

Configuration is managed through environment variables, using the `SERVICE__` prefix with `__` separating nesting levels. Copy `.env.example` to `.env` and customize as needed:

```bash
cp .env.example .env
```

- `SERVICE__AUTH__GOOGLE__CLIENT_ID` - Google OAuth 2.0 client ID used to verify Google Sign-In ID tokens (see [Google Sign-In](../../documentation/services/google-sign-in.md))
- `SERVICE__HTTP__CORS__ALLOW_ORIGINS` - JSON array of allowed browser origins, set by Terraform in deployed environments

`SERVICE__HTTP__RELOAD` is accepted for parity with the documented configuration tree but has no effect — the server has no hot-reload support, and enabling it only logs a warning at startup.
