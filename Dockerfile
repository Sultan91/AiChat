# Build stage
FROM python:3.11-slim as builder

# Install Poetry
ENV POETRY_VERSION=1.6.1 \
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN /opt/poetry/bin/poetry install --only main --no-interaction --no-ansi

# Runtime stage
FROM python:3.11-slim

# Create a non-root user
RUN addgroup --system appgroup && \
    adduser --system --no-create-home --disabled-login --group appuser

WORKDIR /app

# Create data directory for SQLite
RUN mkdir -p /app/data && \
    chown -R appuser:appgroup /app/data

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app \
    PORT=8000 \
    HOST=0.0.0.0 \
    ENVIRONMENT=production \
    LOG_LEVEL=info \
    DATABASE_URL=sqlite+aiosqlite:////app/data/db.sqlite

# Set file permissions
RUN chown -R appuser:appgroup /app \
    && chmod +x /app/docker-entrypoint.sh

# Switch to non-root user
USER appuser

# Create the database file with proper permissions
RUN touch /app/data/db.sqlite && \
    chmod 664 /app/data/db.sqlite

# Expose the port the app runs on
EXPOSE $PORT

# Command to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]