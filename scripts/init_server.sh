#!/bin/bash

# Server initialization script for first-time setup
# Usage: Run this on your VPS after fresh install
# curl -fsSL https://raw.githubusercontent.com/yourusername/learn_pandas_bot/main/scripts/init_server.sh | bash

set -e

echo "🔧 Initializing server for deployment..."

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

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root (use sudo)"
    exit 1
fi

# Update system
print_info "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install required packages
print_info "Installing required packages..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    ufw

# Install Docker
print_info "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    print_info "Docker installed ✓"
else
    print_warning "Docker already installed"
fi

# Install Docker Compose
print_info "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    print_info "Docker Compose installed ✓"
else
    print_warning "Docker Compose already installed"
fi

# Configure firewall
print_info "Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

print_info "Firewall configured ✓"

# Create deployment user (optional)
DEPLOY_USER="deploy"
if ! id "$DEPLOY_USER" &>/dev/null; then
    print_info "Creating deployment user: $DEPLOY_USER"
    useradd -m -s /bin/bash "$DEPLOY_USER"
    usermod -aG docker "$DEPLOY_USER"
    print_info "User $DEPLOY_USER created and added to docker group ✓"
else
    print_warning "User $DEPLOY_USER already exists"
fi

# Create application directory
APP_DIR="/opt/pandas_bot"
print_info "Creating application directory: $APP_DIR"
mkdir -p "$APP_DIR"
chown -R "$DEPLOY_USER:$DEPLOY_USER" "$APP_DIR"

# Setup SSH keys for deployment (optional)
print_info "Setup complete! Next steps:"
echo ""
echo "1. Add SSH keys for deployment user:"
echo "   sudo -u $DEPLOY_USER ssh-keygen -t ed25519"
echo "   Add the public key to GitHub deploy keys"
echo ""
echo "2. Clone your repository:"
echo "   cd $APP_DIR"
echo "   sudo -u $DEPLOY_USER git clone <your-repo-url> ."
echo ""
echo "3. Create .env file with production settings"
echo ""
echo "4. Setup SSL certificates (Let's Encrypt):"
echo "   Use certbot or place certificates in nginx/ssl/"
echo ""
echo "5. Run deployment:"
echo "   ./scripts/deploy.sh"
echo ""

print_info "✅ Server initialization complete!"
