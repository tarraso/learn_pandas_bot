#!/bin/bash

# Database backup script
# Usage: ./scripts/backup.sh

set -e

echo "📦 Starting database backup..."

# Configuration
BACKUP_DIR="./backups"
COMPOSE_FILE="docker-compose.prod.yml"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Load environment variables
if [ -f .env ]; then
    set -a
    source .env
    set +a
else
    print_error ".env file not found!"
    exit 1
fi

# Check if database container is running
if ! docker compose -f "$COMPOSE_FILE" ps db | grep -q "Up"; then
    print_error "Database container is not running!"
    exit 1
fi

# Create backup
print_info "Creating backup: $BACKUP_FILE"

docker compose -f "$COMPOSE_FILE" exec -T db pg_dump \
    -U "${POSTGRES_USER:-user}" \
    -d "${POSTGRES_DB:-pandas_bot_db}" \
    > "$BACKUP_FILE"

# Compress backup
print_info "Compressing backup..."
gzip "$BACKUP_FILE"
BACKUP_FILE="$BACKUP_FILE.gz"

# Check if backup was created successfully
if [ -f "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    print_info "✅ Backup created successfully: $BACKUP_FILE ($BACKUP_SIZE)"
else
    print_error "❌ Backup failed!"
    exit 1
fi

# Keep only last 7 backups
print_info "Cleaning up old backups (keeping last 7)..."
cd "$BACKUP_DIR"
ls -t db_backup_*.sql.gz | tail -n +8 | xargs -r rm
cd - > /dev/null

print_info "📦 Backup completed!"
