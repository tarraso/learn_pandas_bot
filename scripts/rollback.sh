#!/bin/bash

# Rollback script for failed deployments
# Usage: ./scripts/rollback.sh [backup_file]

set -e

echo "⏪ Starting rollback..."

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="./backups"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Stop current containers
print_info "Stopping current containers..."
docker compose -f "$COMPOSE_FILE" down

# Get backup file
if [ -n "$1" ]; then
    BACKUP_FILE="$1"
else
    # Use latest backup
    BACKUP_FILE=$(ls -t "$BACKUP_DIR"/db_backup_*.sql.gz 2>/dev/null | head -n 1)
fi

if [ -z "$BACKUP_FILE" ]; then
    print_error "No backup file found!"
    print_warning "Starting services with current database state..."
    docker compose -f "$COMPOSE_FILE" up -d
    exit 1
fi

print_info "Using backup: $BACKUP_FILE"

# Load environment variables
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Start database container
print_info "Starting database container..."
docker compose -f "$COMPOSE_FILE" up -d db

# Wait for database to be ready
print_info "Waiting for database..."
sleep 10

# Restore database
print_info "Restoring database from backup..."
gunzip -c "$BACKUP_FILE" | docker compose -f "$COMPOSE_FILE" exec -T db psql \
    -U "${POSTGRES_USER:-user}" \
    -d "${POSTGRES_DB:-pandas_bot_db}"

if [ $? -eq 0 ]; then
    print_info "✅ Database restored successfully!"
else
    print_error "❌ Database restore failed!"
    exit 1
fi

# Start all services
print_info "Starting all services..."
docker compose -f "$COMPOSE_FILE" up -d

# Wait for services to be healthy
print_info "Waiting for services to be healthy..."
sleep 10

# Check health
max_attempts=10
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker compose -f "$COMPOSE_FILE" exec -T web python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" 2>/dev/null; then
        print_info "✅ Rollback completed successfully!"
        exit 0
    fi

    attempt=$((attempt + 1))
    print_info "Health check attempt $attempt/$max_attempts..."
    sleep 2
done

print_error "❌ Services failed to become healthy after rollback"
print_error "Please check logs: docker compose -f $COMPOSE_FILE logs"
exit 1
