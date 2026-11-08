# Multi-stage build for the SmartLearn FastAPI backend

# Stage 1: Build stage to compile dependencies and create a clean virtual environment
FROM python:3.12-slim AS builder

# Prevent Python from writing .pyc files and enable unbuffered output for cleaner logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory inside the builder container
WORKDIR /app

# Install compilation tools needed for C-extensions (like bcrypt and libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a clean Python virtual environment
RUN python -m venv /opt/venv

# Add virtual environment binaries to PATH so python and pip use it directly
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements file first to take advantage of Docker layer caching
COPY backend/requirements.txt .

# Upgrade pip and install all Python dependencies into the virtual environment
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# Stage 2: Final minimal runtime stage
FROM python:3.12-slim

# Configure Python runtime environment variables and virtual environment PATH
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Set the working directory for the application
WORKDIR /app

# Install minimal runtime libraries (curl for health check and libpq5 for PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy the pre-built virtual environment with all packages from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create a non-root system user and group for improved container security
RUN useradd -u 10001 -m appuser

# Copy application source code and grant ownership to the non-root user
COPY --chown=appuser:appuser backend/app ./app

# Switch to the non-root user to avoid running the process as root
USER appuser

# Expose the API server port
EXPOSE 8000

# Periodic health check to make sure the FastAPI server is responding on /health
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start uvicorn ASGI server binding to 0.0.0.0 on port 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
