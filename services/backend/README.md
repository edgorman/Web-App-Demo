# Backend Service

A FastAPI backend service for Web-App-Demo with a clean architecture following dependency injection principles.

## Architecture

The backend follows a structured architecture with clear separation of concerns:

```
services/backend/
├── src/
│   ├── cli/              # Command-line interface
│   ├── config/           # Configuration using pydantic settings
│   ├── objects/          # Pydantic models for data objects
│   ├── service/          # Service layer with API interface
│   │   └── fastapi/      # FastAPI implementation
│   │       └── resources/v1/  # API endpoints grouped by version
│   └── storage/          # Storage layer (for future DB integration)
├── tests/                # Tests mirroring src/ structure
└── .env.example          # Environment variable template
```

### Key Design Principles

- **Dependency Injection**: Components are loosely coupled through interfaces
- **Configuration**: Uses pydantic-settings with `.env` file support
- **Type Safety**: Pydantic models for all data objects
- **Testability**: Shared fixtures in conftest.py, tests mirror source structure

## Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Docker (optional, for containerized deployment)

## Setup

Install dependencies:

```bash
make install
```

Or using uv directly:

```bash
uv sync --extra dev
```

## Running the Service

### Local Development

Start the development server:

```bash
make run
```

Or using the CLI:

```bash
uv run python -m src.cli.cli run
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

Run code linting:

```bash
make lint
```

### Testing

Run tests:

```bash
make test
```

## API Endpoints

- `GET /api/v1/hello` - Returns a welcome message

## Configuration

Configuration is managed through environment variables. Copy `.env.example` to `.env` and customize as needed:

```bash
cp .env.example .env
```
