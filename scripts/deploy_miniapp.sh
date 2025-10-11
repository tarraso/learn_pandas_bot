#!/bin/bash

# Deploy miniapp (React frontend) to VPS
# Usage: ./scripts/deploy_miniapp.sh

set -e  # Exit on error

# Configuration
VPS_HOST="${VPS_HOST:-94.72.140.27}"
VPS_USER="${VPS_USER:-root}"
VPS_WEBAPP_DIR="/opt/pandas_bot/webapp/dist"
LOCAL_WEBAPP_DIR="webapp"
TEMP_ARCHIVE="/tmp/miniapp-dist-$(date +%Y%m%d_%H%M%S).tar.gz"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Banner
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Miniapp Deployment Script           ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo ""

# Step 1: Check if webapp directory exists
print_step "Checking webapp directory..."
if [ ! -d "$LOCAL_WEBAPP_DIR" ]; then
    print_error "Webapp directory not found: $LOCAL_WEBAPP_DIR"
    exit 1
fi
print_info "Webapp directory found ✓"

# Step 2: Build the React app
print_step "Building React miniapp..."
cd "$LOCAL_WEBAPP_DIR"
npm run build
if [ ! -d "dist" ]; then
    print_error "Build failed - dist directory not created"
    exit 1
fi
print_info "Build completed ✓"

# Step 3: Package the built files
print_step "Packaging dist files..."
tar -czf "$TEMP_ARCHIVE" -C dist .
ARCHIVE_SIZE=$(du -h "$TEMP_ARCHIVE" | cut -f1)
print_info "Package created: $ARCHIVE_SIZE ✓"
cd ..

# Step 4: Test SSH connection
print_step "Testing SSH connection to $VPS_USER@$VPS_HOST..."
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "$VPS_USER@$VPS_HOST" "echo 'SSH OK'" &>/dev/null; then
    print_error "Cannot connect to VPS. Please check your SSH configuration."
    rm -f "$TEMP_ARCHIVE"
    exit 1
fi
print_info "SSH connection successful ✓"

# Step 5: Upload to VPS
print_step "Uploading to VPS..."
scp "$TEMP_ARCHIVE" "$VPS_USER@$VPS_HOST:/tmp/"
print_info "Upload completed ✓"

# Step 6: Deploy on VPS
print_step "Deploying on VPS..."
ssh "$VPS_USER@$VPS_HOST" bash << EOF
    set -e

    # Backup current deployment
    if [ -d "$VPS_WEBAPP_DIR" ]; then
        echo "Creating backup..."
        BACKUP_DIR="/opt/pandas_bot/backups/webapp-\$(date +%Y%m%d_%H%M%S)"
        mkdir -p "\$BACKUP_DIR"
        cp -r "$VPS_WEBAPP_DIR" "\$BACKUP_DIR/" 2>/dev/null || true
        echo "Backup created at \$BACKUP_DIR"
    fi

    # Create webapp directory if it doesn't exist
    mkdir -p "$VPS_WEBAPP_DIR"

    # Extract new files
    echo "Extracting files..."
    cd "$VPS_WEBAPP_DIR"
    rm -rf *
    tar -xzf "$TEMP_ARCHIVE"

    # Clean up
    rm -f "$TEMP_ARCHIVE"

    # Verify deployment
    if [ -f "index.html" ]; then
        echo "Deployment verified ✓"
    else
        echo "ERROR: Deployment verification failed!"
        exit 1
    fi
EOF

print_info "Deployment on VPS completed ✓"

# Step 7: Clean up local temp file
print_step "Cleaning up..."
rm -f "$TEMP_ARCHIVE"
print_info "Cleanup completed ✓"

# Step 8: Verify deployment
print_step "Verifying deployment..."
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' "http://$VPS_HOST/" || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    print_info "Miniapp is accessible at http://$VPS_HOST/ ✓"
else
    print_warning "HTTP status: $HTTP_CODE - Please check nginx configuration"
fi

# Success message
echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Deployment Completed Successfully!  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "🌐 Miniapp URL: ${BLUE}http://$VPS_HOST/${NC}"
echo -e "📊 Check logs: ${BLUE}ssh $VPS_USER@$VPS_HOST 'docker logs miniapp-nginx'${NC}"
echo ""
