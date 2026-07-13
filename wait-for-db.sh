#!/bin/bash
set -e

host="$DB_HOST"
port="$DB_PORT"

echo "Waiting for PostgreSQL at $host:$port..."

# We use python to attempt connection since we don't have pg_isready installed in the final stage
until python -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.connect(('$host', int('$port')))" 2>/dev/null; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
