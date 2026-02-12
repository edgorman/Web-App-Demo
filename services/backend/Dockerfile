# Build stage - Install dependencies
FROM python:3.13-slim AS builder

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Create a minimal setup for installation
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir hatchling && \
    pip install --no-cache-dir .

# Runtime stage
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Get Python version dynamically
ARG PYTHON_VERSION=3.13
ENV PYTHON_VERSION=${PYTHON_VERSION}

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python${PYTHON_VERSION}/site-packages /usr/local/lib/python${PYTHON_VERSION}/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY main.py ./

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
