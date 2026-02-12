# Backend Service

A basic FastAPI backend service for Web-App-Demo.

## Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager

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

Start the development server:

```bash
make run
```

Or using uv directly:

```bash
uv run uvicorn main:app --reload
```

The service will be available at `http://127.0.0.1:8000`

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
