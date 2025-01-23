#!/bin/bash

# Check if environment variables are set
if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "Error: POSTGRES_PASSWORD environment variable is not set"
    exit 1
fi

export PGPASSWORD="$POSTGRES_PASSWORD"

# Drop types from default database (postgres)
psql -h "${POSTGRES_SERVER:-localhost}" -U "${POSTGRES_USER:-postgres}" -c "DROP TYPE IF EXISTS monitoring_status CASCADE;"
psql -h "${POSTGRES_SERVER:-localhost}" -U "${POSTGRES_USER:-postgres}" -c "DROP TYPE IF EXISTS video_processing_status CASCADE;"
psql -h "${POSTGRES_SERVER:-localhost}" -U "${POSTGRES_USER:-postgres}" -c "DROP TYPE IF EXISTS monitoring_interval CASCADE;"

# Drop and recreate holyvoice database
psql -h "${POSTGRES_SERVER:-localhost}" -U "${POSTGRES_USER:-postgres}" -c "DROP DATABASE IF EXISTS ${POSTGRES_DB:-holyvoice};"
psql -h "${POSTGRES_SERVER:-localhost}" -U "${POSTGRES_USER:-postgres}" -c "CREATE DATABASE ${POSTGRES_DB:-holyvoice};"

# Drop types from holyvoice database
psql -h "${POSTGRES_SERVER:-localhost}" -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-holyvoice}" -c "DROP TYPE IF EXISTS monitoring_status CASCADE;"
psql -h "${POSTGRES_SERVER:-localhost}" -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-holyvoice}" -c "DROP TYPE IF EXISTS video_processing_status CASCADE;"
psql -h "${POSTGRES_SERVER:-localhost}" -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-holyvoice}" -c "DROP TYPE IF EXISTS monitoring_interval CASCADE;"

# Run migrations
alembic upgrade head
