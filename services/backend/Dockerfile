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

# Accept frontend URL as build argument
ARG FRONTEND_URL

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src ./src

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Set CORS origins from build argument
# Write to shell script that will be sourced at container start
RUN printf '#!/bin/sh\nexport SERVICE__FASTAPI__CORS__ALLOW_ORIGINS='"'"'["%s"]'"'"'\nexec "$@"\n' "$FRONTEND_URL" > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh && \
    cat /app/entrypoint.sh

# Expose port (can be overridden by SERVICE__FASTAPI__PORT env var)
ARG PORT=8080
EXPOSE ${PORT}

# Use entrypoint to set environment variable, then run the application
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "-m", "src.cli.cli", "run"]
