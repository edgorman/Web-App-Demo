# Build stage - Install dependencies
ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies using uv
RUN uv sync --no-dev

# Runtime stage
FROM python:${PYTHON_VERSION}-slim

# Set working directory
WORKDIR /app

# Set Python version environment variable
ENV PYTHON_VERSION=${PYTHON_VERSION}

# Accept frontend URL as build argument (required)
ARG FRONTEND_URL

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src ./src

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Set CORS origins from build argument
# Validate that FRONTEND_URL is provided, not empty, and has valid URL format
RUN if [ -z "$FRONTEND_URL" ]; then \
      echo "ERROR: FRONTEND_URL build argument is required but was not provided" >&2; \
      exit 1; \
    fi && \
    case "$FRONTEND_URL" in \
      http://*|https://*) ;; \
      *) echo "ERROR: FRONTEND_URL must start with http:// or https://" >&2; exit 1 ;; \
    esac && \
    echo "$FRONTEND_URL" > /app/.frontend_url && \
    printf '%s\n' \
      '#!/bin/sh' \
      'FRONTEND_URL=$(cat /app/.frontend_url)' \
      'export SERVICE__FASTAPI__CORS__ALLOW_ORIGINS="[\"$FRONTEND_URL\"]"' \
      'exec "$@"' \
      > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh && \
    echo "Created entrypoint with CORS origin: $FRONTEND_URL"

# Expose port (can be overridden by SERVICE__FASTAPI__PORT env var)
ARG PORT=8080
EXPOSE ${PORT}

# Use entrypoint to set environment variable, then run the application
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "-m", "src.cli.cli", "run"]
