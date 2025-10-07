#!/bin/bash

# Setup swap file for low memory VPS
# Usage: sudo ./scripts/setup_swap.sh [size_in_gb]

set -e

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

# Get swap size (default 1GB)
SWAP_SIZE=${1:-1}
SWAP_FILE="/swapfile"

print_info "Setting up ${SWAP_SIZE}GB swap file..."

# Check if swap already exists
if [ -f "$SWAP_FILE" ]; then
    print_warning "Swap file already exists at $SWAP_FILE"
    read -p "Do you want to recreate it? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Keeping existing swap file"
        exit 0
    fi

    print_info "Removing existing swap..."
    swapoff "$SWAP_FILE" 2>/dev/null || true
    rm "$SWAP_FILE"
fi

# Create swap file
print_info "Creating ${SWAP_SIZE}GB swap file..."
fallocate -l ${SWAP_SIZE}G "$SWAP_FILE" || dd if=/dev/zero of="$SWAP_FILE" bs=1M count=$((SWAP_SIZE * 1024))

# Set permissions
print_info "Setting permissions..."
chmod 600 "$SWAP_FILE"

# Setup swap
print_info "Setting up swap..."
mkswap "$SWAP_FILE"
swapon "$SWAP_FILE"

# Verify swap
print_info "Verifying swap..."
swapon --show
free -h

# Make swap permanent
if ! grep -q "$SWAP_FILE" /etc/fstab; then
    print_info "Adding swap to /etc/fstab..."
    echo "$SWAP_FILE none swap sw 0 0" >> /etc/fstab
fi

# Optimize swappiness for VPS
print_info "Optimizing swap settings..."
sysctl vm.swappiness=10
sysctl vm.vfs_cache_pressure=50

# Make swappiness permanent
if ! grep -q "vm.swappiness" /etc/sysctl.conf; then
    echo "vm.swappiness=10" >> /etc/sysctl.conf
    echo "vm.vfs_cache_pressure=50" >> /etc/sysctl.conf
fi

print_info "✅ Swap setup complete!"
print_info "Current memory status:"
free -h
