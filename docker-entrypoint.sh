#!/bin/bash
set -e

echo "Running Alembic migrations..."
alembic upgrade head || echo "WARNING: Alembic upgrade failed. Continuing anyway."

echo "Starting application..."
exec "$@"
