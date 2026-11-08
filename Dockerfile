# ==============================================================================
# SmartLearn API - Production Dockerfile (Root)
# ==============================================================================
# Multi-stage build designed for security, minimal attack surface, and fast builds:
#   - Stage 1 (builder): Installs build tools, compiles wheels, and creates a venv.
#   - Stage 2 (runner):  Copies the venv, sets up a non-root user, and runs uvicorn.
# ==============================================================================

# ------------------------------------------------------------------------------
# STAGE 1: Builder
# ------------------------------------------------------------------------------
# Use a specific Debian-slim base image (pinned version) for reproducibility and small size
FROM python:3.12-slim AS builder

# Prevent Python from writing .pyc bytecode and force unbuffered stdout/stderr logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set intermediate build working directory
WORKDIR /build

# Install minimal build dependencies needed for compiled Python extensions (psycopg, bcrypt)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create isolated Python virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy dependency manifest first to leverage Docker layer caching (avoid re-installing on code changes)
COPY backend/requirements.txt /build/requirements.txt

# Upgrade pip and install all Python dependencies into the isolated virtual environment
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /build/requirements.txt


# ------------------------------------------------------------------------------
# STAGE 2: Production Runtime
# ------------------------------------------------------------------------------
# Start from a clean, minimal runtime base image
FROM python:3.12-slim AS runner

# Set essential runtime environment flags
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/app

# Define production working directory
WORKDIR /app

# Install runtime dependencies only (curl for container health checks, libpq5 for PostgreSQL driver)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-compiled virtual environment from builder stage (no build tools in runtime image)
COPY --from=builder /opt/venv /opt/venv

# Create a dedicated non-root user and group with explicit UID/GID for security best practices
# Running as non-root mitigates container escape vulnerabilities
RUN groupadd --gid 10001 appgroup && \
    useradd --uid 10001 --gid appgroup --shell /bin/bash --create-home appuser

# Copy application source code into the container with non-root ownership
COPY --chown=appuser:appgroup backend/app /app/app

# Ensure proper non-root directory ownership and permissions
RUN chown -R appuser:appgroup /app

# Switch to the non-root user for all subsequent commands and runtime execution
USER appuser

# Document that the application listens on port 8000
EXPOSE 8000

# Container Healthcheck: continuously verifies that the FastAPI /health endpoint responds
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the FastAPI application using the production Uvicorn ASGI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
