# 🚀 AlphaVPS Setup Guide

Complete guide for deploying on AlphaVPS (budget-friendly option).

## 📦 Why AlphaVPS?

**Pros**:
- ✅ Very affordable ($3-7/mo)
- ✅ Multiple locations (EU, US, Asia)
- ✅ KVM virtualization (Docker compatible)
- ✅ Good for low-traffic projects

**Cons**:
- ⚠️ Lower performance than premium providers
- ⚠️ Support can be slower
- ⚠️ Network can be inconsistent
- ⚠️ Resources sometimes oversold

**Best for**: Personal projects, testing, learning, small bots (<500 daily users)

---

## 🎯 Recommended Plans

### Budget Option (Lite Config)
- **Plan**: KVM SSD VPS - 1GB
- **Specs**: 1 CPU, 1GB RAM, 15GB SSD
- **Price**: ~$5/mo
- **Config**: Use `docker-compose.prod.lite.yml`
- **Users**: <100 concurrent

### Standard Option (PostgreSQL Config)
- **Plan**: KVM SSD VPS - 2GB
- **Specs**: 1-2 CPU, 2GB RAM, 30GB SSD
- **Price**: ~$7/mo
- **Config**: Use `docker-compose.prod.yml`
- **Users**: 100-500 concurrent

---

## 🛠️ Initial Server Setup

### 1. Order VPS

⚠️ **IMPORTANT**: Select **KVM** virtualization, NOT OpenVZ!

```
AlphaVPS Website → Order VPS → Choose:
- Virtualization: KVM (required for Docker!)
- OS: Ubuntu 22.04 LTS
- Location: Choose closest to your users
- Additional: No control panel needed
```

### 2. Access VPS

After order, you'll receive email with:
- IP address
- Root password
- SSH port (usually 22)

```bash
# Connect via SSH
ssh root@YOUR_VPS_IP

# Change root password immediately
passwd
```

### 3. Verify System

```bash
# Check virtualization (should show KVM)
systemd-detect-virt
# Expected output: kvm

# Check resources
free -h
df -h

# Update system
apt-get update && apt-get upgrade -y
```

### 4. Run Initialization Script

```bash
# Download and run init script
curl -fsSL https://raw.githubusercontent.com/yourusername/learn_pandas_bot/main/scripts/init_server.sh | bash
```

Or manually:

```bash
# Install Git
apt-get install -y git

# Clone repo
cd /opt
git clone https://github.com/yourusername/learn_pandas_bot.git pandas_bot
cd pandas_bot

# Run init script
chmod +x scripts/init_server.sh
./scripts/init_server.sh
```

### 5. Setup Swap (CRITICAL!)

AlphaVPS often has tight memory - swap is essential:

```bash
# For 1GB RAM plan
sudo ./scripts/setup_swap.sh 2

# For 2GB RAM plan
sudo ./scripts/setup_swap.sh 1

# Verify
free -h
swapon --show
```

### 6. Configure Firewall

```bash
# UFW should be configured by init script, verify:
sudo ufw status

# Should show:
# 22/tcp (SSH) - ALLOW
# 80/tcp (HTTP) - ALLOW
# 443/tcp (HTTPS) - ALLOW
```

---

## 🔒 Security Hardening

### 1. Create Non-Root User

```bash
# Create deploy user
useradd -m -s /bin/bash deploy
usermod -aG docker,sudo deploy

# Set password
passwd deploy

# Switch to deploy user
su - deploy
```

### 2. SSH Key Authentication (Recommended)

On your local machine:

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "deploy@alphavps"

# Copy to server
ssh-copy-id deploy@YOUR_VPS_IP
```

On server, disable password auth:

```bash
sudo nano /etc/ssh/sshd_config

# Change these lines:
PasswordAuthentication no
PermitRootLogin no

# Restart SSH
sudo systemctl restart sshd
```

### 3. Fail2Ban (Optional but Recommended)

```bash
sudo apt-get install -y fail2ban

# Configure
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local

# Enable for SSH:
[sshd]
enabled = true
maxretry = 3

# Restart
sudo systemctl restart fail2ban
```

---

## 🚀 Deploy Application

### Option A: Lite Configuration (1GB RAM)

```bash
cd /opt/pandas_bot

# Create .env
cp .env.example .env
nano .env

# Set:
DJANGO_ENV=production
DEBUG=False
SECRET_KEY=<generate-strong-key>
DATABASE_URL=sqlite:////app/data/db.sqlite3
ALLOWED_HOSTS=yourdomain.com
WEBAPP_URL=https://yourdomain.com
TELEGRAM_BOT_TOKEN=<your-token>

# Create data directory
mkdir -p data

# Build and deploy
docker compose -f docker-compose.prod.lite.yml build
docker compose -f docker-compose.prod.lite.yml up -d

# Run migrations
docker compose -f docker-compose.prod.lite.yml exec app python manage.py migrate

# Check status
docker compose -f docker-compose.prod.lite.yml ps
```

### Option B: Standard Configuration (2GB RAM)

```bash
cd /opt/pandas_bot

# Create .env
cp .env.example .env
nano .env

# Set:
DJANGO_ENV=production
DEBUG=False
SECRET_KEY=<generate-strong-key>
POSTGRES_PASSWORD=<generate-strong-password>
ALLOWED_HOSTS=yourdomain.com
WEBAPP_URL=https://yourdomain.com
TELEGRAM_BOT_TOKEN=<your-token>

# Build and deploy
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# Run migrations
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Check status
docker compose -f docker-compose.prod.yml ps
```

---

## 📊 Performance Monitoring

### Monitor Memory Usage

```bash
# Real-time system stats
htop

# Docker container stats
docker stats

# Memory check
free -h

# Check if services are being OOM killed
dmesg | grep -i "out of memory"
```

### Optimize if Needed

If memory usage is high (>90%):

1. **Add more swap**:
   ```bash
   sudo ./scripts/setup_swap.sh 2
   ```

2. **Reduce Gunicorn workers** (edit docker-compose):
   ```yaml
   command: gunicorn ... --workers 1 --threads 4
   ```

3. **Use Lite config** instead of Standard

4. **Clean Docker cache**:
   ```bash
   docker system prune -a -f
   ```

### Monitor Logs

```bash
# Application logs
docker compose logs -f

# Check for errors
docker compose logs | grep -i error

# System logs
journalctl -xe
```

---

## 🐛 Troubleshooting AlphaVPS Specific Issues

### Issue: "Cannot connect to Docker daemon"

```bash
# Check Docker service
sudo systemctl status docker

# If not running
sudo systemctl start docker
sudo systemctl enable docker

# Check virtualization
systemd-detect-virt
# If shows "openvz" - you ordered wrong plan!
```

### Issue: Services keep restarting

```bash
# Check OOM killer
dmesg | tail -50

# If out of memory:
1. Add/increase swap
2. Use Lite config
3. Reduce workers
4. Consider upgrading plan
```

### Issue: Slow performance

AlphaVPS can have variable performance:

```bash
# Test disk I/O
dd if=/dev/zero of=test bs=64k count=16k conv=fdatasync
rm test

# Expected: 200-500 MB/s for SSD

# Test network
apt-get install speedtest-cli
speedtest-cli

# If very slow:
- Contact AlphaVPS support
- Consider changing location
- Check for maintenance announcements
```

### Issue: Docker build fails with "no space left"

```bash
# Check disk usage
df -h

# Clean Docker
docker system prune -a -f
docker volume prune -f

# If still full:
- Delete old logs: rm -rf logs/*.log
- Consider larger storage plan
```

---

## 💡 AlphaVPS Best Practices

1. **Always use swap** - essential on budget VPS
2. **Monitor first week** - check for stability issues
3. **Backup regularly** - use `./scripts/backup.sh`
4. **Keep updated** - `apt-get update && apt-get upgrade`
5. **Use Lite config** for 1GB plans
6. **Test before production** - verify performance with load

---

## 📈 Scaling on AlphaVPS

### When to Upgrade

Signs you need more resources:
- Memory usage consistently >85%
- Services restart frequently
- Slow response times (>2s)
- Bot messages delayed
- OOM errors in logs

### Upgrade Path

1. **Start**: 1GB RAM with Lite config ($5/mo)
   - 0-50 users

2. **Upgrade**: 2GB RAM with Standard config ($7/mo)
   - 50-200 users

3. **Scale**: 4GB RAM with Standard config ($12/mo)
   - 200-500 users

4. **Move**: Premium provider (Hetzner, DO) when >500 users
   - Better performance
   - Superior support
   - More reliable

---

## 🔗 Useful Links

- [AlphaVPS Website](https://alphavps.com/)
- [AlphaVPS Status Page](https://status.alphavps.com/)
- [Client Area](https://my.alphavps.com/)
- [Looking Glass](https://lg.alphavps.com/) - Test network speed

---

## 💬 Community Feedback

AlphaVPS is generally reliable for small projects but:
- Expect occasional network hiccups
- Support response: 12-48 hours
- Performance varies by location
- Great for learning/testing
- Consider premium provider for serious production

**Bottom line**: Perfect for starting out, plan to migrate if project grows.
