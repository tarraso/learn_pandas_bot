#!/bin/bash

# Production deployment script
# Usage: ./scripts/deploy.sh

set -e  # Exit on error

echo "🚀 Starting deployment..."

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="./backups"
PROJECT_NAME="pandas_bot"

# Colors for output
RED='\033[0:31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found!"
    print_info "Please create .env file from .env.example"
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

# Validate required environment variables
required_vars=("SECRET_KEY" "POSTGRES_PASSWORD" "TELEGRAM_BOT_TOKEN" "ALLOWED_HOSTS" "WEBAPP_URL")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        print_error "Required environment variable $var is not set!"
        exit 1
    fi
done

print_info "Environment variables validated ✓"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Backup database before deployment
print_info "Creating database backup..."
./scripts/backup.sh || print_warning "Backup failed, continuing with deployment..."

# Pull latest changes from git (if in git repo)
if [ -d .git ]; then
    print_info "Pulling latest changes..."
    git pull origin main || print_warning "Git pull failed, using local code"
fi

# Build and pull images
print_info "Building Docker images..."
docker compose -f "$COMPOSE_FILE" build --no-cache

# Stop existing containers
print_info "Stopping existing containers..."
docker compose -f "$COMPOSE_FILE" down

# Start services
print_info "Starting services..."
docker compose -f "$COMPOSE_FILE" up -d

# Wait for services to be healthy
print_info "Waiting for services to be healthy..."
sleep 10

# Run database migrations
print_info "Running database migrations..."
docker compose -f "$COMPOSE_FILE" exec -T web python manage.py migrate --noinput

# Check health
print_info "Checking application health..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker compose -f "$COMPOSE_FILE" exec -T web python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" 2>/dev/null; then
        print_info "✅ Application is healthy!"
        break
    fi

    attempt=$((attempt + 1))
    if [ $attempt -eq $max_attempts ]; then
        print_error "❌ Health check failed after $max_attempts attempts"
        print_error "Rolling back deployment..."
        ./scripts/rollback.sh
        exit 1
    fi

    print_info "Health check attempt $attempt/$max_attempts..."
    sleep 2
done

# Clean up old images
print_info "Cleaning up old Docker images..."
docker image prune -f

# Show running containers
print_info "Running containers:"
docker compose -f "$COMPOSE_FILE" ps

print_info "✅ Deployment completed successfully!"
print_info "📊 View logs: docker compose -f $COMPOSE_FILE logs -f"
