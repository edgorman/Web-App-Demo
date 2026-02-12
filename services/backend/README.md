# Backend Service

A basic FastAPI backend service for Web-App-Demo.

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
uv sync
```

## Running the Service

### Local Development

Start the development server:

```bash
make run
```

Or using uv directly:

```bash
uv run uvicorn main:app --reload
```

The service will be available at `http://127.0.0.1:8000`

### Docker

Build the Docker image:

```bash
docker build -t web-app-demo-backend .
```

Run the container:

```bash
docker run -d -p 8000:8000 --name backend web-app-demo-backend
```

The service will be available at `http://localhost:8000`

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

- `GET /` - Returns a welcome message
