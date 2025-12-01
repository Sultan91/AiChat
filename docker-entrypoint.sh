#!/bin/sh
set -e

# Create data directory if it doesn't exist
mkdir -p /app/data

# Check if database file exists, if not create it
if [ ! -f "/app/data/db.sqlite" ]; then
    echo "Creating new SQLite database..."
    touch /app/data/db.sqlite
    chmod 664 /app/data/db.sqlite
fi

# Run migrations
cd /app
alembic upgrade head

# Execute the CMD from docker-compose
exec "$@"