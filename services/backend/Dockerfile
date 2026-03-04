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
# If FRONTEND_URL is empty, create empty list, otherwise include the URL
RUN if [ -n "$FRONTEND_URL" ]; then \
      echo "SERVICE__FASTAPI__CORS__ALLOW_ORIGINS=[\"$FRONTEND_URL\"]" > /app/.env; \
    else \
      echo "SERVICE__FASTAPI__CORS__ALLOW_ORIGINS=[]" > /app/.env; \
    fi

# Expose port (can be overridden by SERVICE__FASTAPI__PORT env var)
ARG PORT=8080
EXPOSE ${PORT}

# Run the application
CMD ["python", "-m", "src.cli.cli", "run"]
