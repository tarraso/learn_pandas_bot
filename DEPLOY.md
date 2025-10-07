# 🚀 Production Deployment Guide

This guide covers deploying the Pandas Learning Bot to a production VPS with Docker, Nginx, and automated CI/CD via GitHub Actions.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [SSL Certificates](#ssl-certificates)
4. [Environment Configuration](#environment-configuration)
5. [GitHub Actions Setup](#github-actions-setup)
6. [Manual Deployment](#manual-deployment)
7. [Maintenance](#maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required

- **VPS Server**: Ubuntu 22.04+ with **KVM virtualization**
  - ⚠️ **Important**: Must be KVM, not OpenVZ (Docker requires full virtualization)
- **Domain**: Pointed to your VPS IP address
- **Telegram Bot Token**: From [@BotFather](https://t.me/BotFather)
- **GitHub Account**: For CI/CD

### VPS Recommendations & Pricing

| Configuration | CPU | RAM | Storage | Provider | Price/mo | Notes |
|--------------|-----|-----|---------|----------|----------|-------|
| **Lite (SQLite)** | 1 | 512MB-1GB | 10-15GB | AlphaVPS (KVM) | $3-5 | Budget option |
| | 1 | 2GB | 20GB | Hetzner CX11 | €4 | Premium, fast |
| **Standard (PostgreSQL)** | 1-2 | 1-2GB | 20-30GB | AlphaVPS (KVM) | $5-7 | Good value |
| | 2 | 4GB | 40GB | Hetzner CX22 | €6 | Premium, reliable |
| **Recommended** | 2 | 2-4GB | 30-40GB | AlphaVPS / Hetzner | $7-12 | Growth ready |

**AlphaVPS Tips**:
- ✅ Choose **KVM** plans (NOT OpenVZ)
- ✅ European locations faster for EU users
- ✅ Check reviews - performance varies
- ✅ Add swap (essential on budget VPS)

### Optional

- **OpenAI API Key**: For additional content generation
- **Monitoring**: Sentry, Uptime Robot, etc.

---

## Server Setup

### Option 1: Automated Setup (Recommended)

Run the initialization script on your fresh VPS:

```bash
# As root or with sudo
curl -fsSL https://raw.githubusercontent.com/yourusername/learn_pandas_bot/main/scripts/init_server.sh | sudo bash
```

This script will:
- Install Docker and Docker Compose
- Configure firewall (UFW)
- Create deployment user
- Set up application directory

### Option 2: Manual Setup

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Configure firewall
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Create deployment user
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy
sudo mkdir -p /opt/pandas_bot
sudo chown -R deploy:deploy /opt/pandas_bot
```

### Clone Repository

```bash
# Switch to deployment user
sudo -u deploy -i

# Clone repository
cd /opt/pandas_bot
git clone https://github.com/yourusername/learn_pandas_bot.git .
```

### Setup Swap (REQUIRED for AlphaVPS, Recommended for all <2GB RAM)

⚠️ **Critical for budget VPS** - prevents OOM crashes:

```bash
# For 512MB-1GB RAM: add 2GB swap
sudo ./scripts/setup_swap.sh 2

# For 2GB RAM: add 1GB swap
sudo ./scripts/setup_swap.sh 1
```

**Why swap is important**:
- Budget VPS often have memory spikes
- Docker builds can use extra memory
- Prevents sudden crashes during deployment
- Acts as safety buffer for PostgreSQL

**On AlphaVPS specifically**:
- Check `free -h` after setup to verify swap is active
- Monitor with `htop` during first few days
- If services are killed, increase swap size

---

## SSL Certificates

### Using Let's Encrypt (Recommended)

#### Method 1: Certbot

```bash
# Install certbot
sudo apt-get install certbot

# Generate certificates
sudo certbot certonly --standalone -d yourdomain.com

# Copy to nginx directory
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/
sudo chown -R deploy:deploy nginx/ssl/
```

#### Method 2: Docker Certbot

```bash
# Using Docker
docker run -it --rm \
  -v $(pwd)/nginx/ssl:/etc/letsencrypt \
  -p 80:80 \
  certbot/certbot certonly \
  --standalone \
  -d yourdomain.com
```

### Auto-renewal

Add to crontab:

```bash
sudo crontab -e
```

Add this line:

```
0 0 1 * * certbot renew --quiet && cd /opt/pandas_bot && docker compose -f docker-compose.prod.yml restart nginx
```

### Using HTTP-only (Not Recommended for Production)

If you don't have SSL certificates yet:

```bash
# Use HTTP-only nginx config
cd nginx/conf.d
cp default.http-only.conf.example default.conf
```

---

## Environment Configuration

### 1. Create Production .env File

```bash
cd /opt/pandas_bot
cp .env.example .env
nano .env
```

### 2. Configure Required Variables

```bash
# ===== CRITICAL SETTINGS =====
DJANGO_ENV=production
DEBUG=False

# Generate strong secret key
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Your domain
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
WEBAPP_URL=https://yourdomain.com

# ===== DATABASE =====
POSTGRES_DB=pandas_bot_db
POSTGRES_USER=user
POSTGRES_PASSWORD=<generate-strong-password>

# ===== TELEGRAM =====
TELEGRAM_BOT_TOKEN=<your-bot-token>

# ===== OPTIONAL =====
OPENAI_API_KEY=<your-openai-key>
CORS_ADDITIONAL_ORIGINS=
```

### 3. Verify Configuration

```bash
# Test environment loading
docker compose -f docker-compose.prod.yml config
```

---

## GitHub Actions Setup

### 1. Add GitHub Secrets

Go to **Settings → Secrets and variables → Actions** in your repository and add:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `SECRET_KEY` | Django secret key | (generated string) |
| `ALLOWED_HOSTS` | Comma-separated domains | `yourdomain.com,www.yourdomain.com` |
| `WEBAPP_URL` | Full webapp URL | `https://yourdomain.com` |
| `POSTGRES_PASSWORD` | Database password | (strong password) |
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather | `123456:ABC-DEF...` |
| `OPENAI_API_KEY` | OpenAI API key (optional) | `sk-...` |
| `VPS_HOST` | VPS IP or hostname | `123.45.67.89` |
| `VPS_USER` | SSH user | `deploy` |
| `VPS_SSH_KEY` | Private SSH key | (entire key content) |
| `VPS_APP_DIR` | App directory | `/opt/pandas_bot` |
| `VPS_PORT` | SSH port | `22` |
| `DOMAIN` | Your domain | `yourdomain.com` |

### 2. Generate SSH Key

On your VPS:

```bash
# As deploy user
sudo -u deploy -i
ssh-keygen -t ed25519 -C "github-actions"

# Add to authorized_keys
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys

# Copy private key to GitHub secrets
cat ~/.ssh/id_ed25519
```

### 3. Test GitHub Actions

Push to `main` branch:

```bash
git push origin main
```

Check **Actions** tab in GitHub to see deployment progress.

---

## Manual Deployment

### First Deployment

Choose your configuration based on VPS specs:

#### Option A: Standard (PostgreSQL) - For 1GB+ RAM

```bash
cd /opt/pandas_bot

# Build and start services
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# Run migrations
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Create superuser (optional)
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Check status
docker compose -f docker-compose.prod.yml ps
```

**Memory usage**: ~600-800MB total
- PostgreSQL: ~100-150MB
- Django (2 workers): ~200-250MB
- Bot: ~100-150MB
- Nginx: ~10-20MB

#### Option B: Lite (SQLite) - For 512MB-1GB RAM

```bash
cd /opt/pandas_bot

# Create data directory for SQLite
mkdir -p data

# Build and start services
docker compose -f docker-compose.prod.lite.yml build
docker compose -f docker-compose.prod.lite.yml up -d

# Run migrations (inside combined container)
docker compose -f docker-compose.prod.lite.yml exec app python manage.py migrate

# Create superuser (optional)
docker compose -f docker-compose.prod.lite.yml exec app python manage.py createsuperuser

# Check status
docker compose -f docker-compose.prod.lite.yml ps
```

**Memory usage**: ~400-500MB total
- App (Django + Bot combined): ~300-350MB
- Nginx: ~10-20MB

**Note**: Lite version combines web and bot into one container and uses SQLite instead of PostgreSQL. Perfect for small VPS but limited to ~100 concurrent users.

### Using Deploy Script

Standard (PostgreSQL):
```bash
./scripts/deploy.sh
```

Lite (SQLite) - modify script to use lite config:
```bash
# Edit deploy.sh and change COMPOSE_FILE
COMPOSE_FILE="docker-compose.prod.lite.yml"
./scripts/deploy.sh
```

This script automatically:
- Creates database backup (PostgreSQL only)
- Builds Docker images
- Runs migrations
- Performs health checks
- Rolls back on failure

---

## Maintenance

### View Logs

Standard (PostgreSQL):
```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml logs -f bot
docker compose -f docker-compose.prod.yml logs -f nginx

# Django logs
tail -f logs/django.log
```

Lite (SQLite):
```bash
# All services
docker compose -f docker-compose.prod.lite.yml logs -f

# Specific services
docker compose -f docker-compose.prod.lite.yml logs -f app
docker compose -f docker-compose.prod.lite.yml logs -f nginx
```

### Database Backup

**PostgreSQL only** (standard config):
```bash
# Manual backup
./scripts/backup.sh

# Backups are stored in ./backups/
ls -lh backups/
```

**SQLite** (lite config):
```bash
# Simple file copy backup
sudo cp data/db.sqlite3 data/db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)

# Compress
gzip data/db.sqlite3.backup.*
```

### Database Restore

**PostgreSQL**:
```bash
# Automatic (uses latest backup)
./scripts/rollback.sh

# Manual (specify backup file)
./scripts/rollback.sh backups/db_backup_20240107_123456.sql.gz
```

**SQLite**:
```bash
# Stop containers
docker compose -f docker-compose.prod.lite.yml down

# Restore backup
gunzip -c data/db.sqlite3.backup.YYYYMMDD_HHMMSS.gz > data/db.sqlite3

# Start containers
docker compose -f docker-compose.prod.lite.yml up -d
```

### Update Application

#### Via GitHub Actions (Recommended)

Just push to `main` branch:

```bash
git push origin main
```

#### Manual Update

```bash
cd /opt/pandas_bot

# Pull latest code
git pull origin main

# Run deployment
./scripts/deploy.sh
```

### Restart Services

```bash
# All services
docker compose -f docker-compose.prod.yml restart

# Specific service
docker compose -f docker-compose.prod.yml restart web
docker compose -f docker-compose.prod.yml restart bot
```

### Stop Services

```bash
docker compose -f docker-compose.prod.yml down
```

### Clean Up

```bash
# Remove stopped containers
docker container prune -f

# Remove unused images
docker image prune -a -f

# Remove unused volumes (BE CAREFUL!)
docker volume prune -f
```

---

## Troubleshooting

### Check Application Health

```bash
# Health endpoint
curl http://localhost/health/

# Or from external
curl https://yourdomain.com/health/
```

Expected response:
```json
{
  "status": "healthy",
  "checks": {
    "database": "ok"
  }
}
```

### Common Issues

#### Services Won't Start

```bash
# Check logs
docker compose -f docker-compose.prod.yml logs

# Check disk space
df -h

# Check memory
free -h

# Restart Docker
sudo systemctl restart docker
```

#### Database Connection Errors

```bash
# Check database container
docker compose -f docker-compose.prod.yml ps db

# Check database logs
docker compose -f docker-compose.prod.yml logs db

# Connect to database
docker compose -f docker-compose.prod.yml exec db psql -U user -d pandas_bot_db
```

#### Nginx Errors

```bash
# Test nginx config
docker compose -f docker-compose.prod.yml exec nginx nginx -t

# Check nginx logs
docker compose -f docker-compose.prod.yml logs nginx

# Verify SSL certificates
ls -l nginx/ssl/
```

#### Bot Not Responding

```bash
# Check bot logs
docker compose -f docker-compose.prod.yml logs bot

# Verify bot token
docker compose -f docker-compose.prod.yml exec bot python -c "import os; print(os.environ.get('TELEGRAM_BOT_TOKEN'))"

# Restart bot
docker compose -f docker-compose.prod.yml restart bot
```

#### Migrations Failed

```bash
# Check migration status
docker compose -f docker-compose.prod.yml exec web python manage.py showmigrations

# Fake migrations (if needed)
docker compose -f docker-compose.prod.yml exec web python manage.py migrate --fake

# Manual migration
docker compose -f docker-compose.prod.yml exec web python manage.py migrate <app_name>
```

### Performance Monitoring

```bash
# Container stats
docker stats

# Top processes
docker compose -f docker-compose.prod.yml top

# Resource usage
docker compose -f docker-compose.prod.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
```

---

## Security Best Practices

1. **Keep secrets secret**: Never commit `.env` or SSL keys to git
2. **Regular updates**: Update Docker images and system packages
3. **Backup regularly**: Automate database backups
4. **Monitor logs**: Check for suspicious activity
5. **Use strong passwords**: For database and admin accounts
6. **Enable firewall**: Only open necessary ports
7. **SSL/TLS**: Always use HTTPS in production
8. **Rate limiting**: Configure in Nginx for API endpoints

---

## Support & Resources

- **GitHub Issues**: https://github.com/yourusername/learn_pandas_bot/issues
- **Documentation**: See README.md
- **Docker Docs**: https://docs.docker.com/
- **Nginx Docs**: https://nginx.org/en/docs/

---

## License

MIT License - See LICENSE file for details
