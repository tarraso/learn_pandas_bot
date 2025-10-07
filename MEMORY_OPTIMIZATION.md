# 💾 Memory Optimization Guide

This guide explains how to run the bot on minimal VPS configurations (512MB - 1GB RAM).

## 📊 Memory Usage Comparison

### Standard Configuration (PostgreSQL)
**Recommended**: 1GB+ RAM

| Service | Memory Usage |
|---------|-------------|
| PostgreSQL (alpine) | 100-150 MB |
| Django (2 workers + threads) | 200-250 MB |
| Telegram Bot | 100-150 MB |
| Nginx | 10-20 MB |
| **Total** | **~600-800 MB** |

**Use case**: Production with moderate traffic (100-500 concurrent users)

### Lite Configuration (SQLite)
**Recommended**: 512MB - 1GB RAM

| Service | Memory Usage |
|---------|-------------|
| App (Django + Bot combined) | 300-350 MB |
| Nginx | 10-20 MB |
| **Total** | **~400-500 MB** |

**Use case**: Development, testing, or small production (<100 concurrent users)

---

## 🔧 Optimizations Applied

### 1. PostgreSQL Tuning (Standard Config)

```yaml
command: >
  postgres
  -c shared_buffers=128MB        # Reduced from default 256MB
  -c effective_cache_size=256MB  # Reduced from default 4GB
  -c max_connections=20          # Reduced from default 100
  -c work_mem=8MB                # Reduced from default 4MB
  -c maintenance_work_mem=64MB   # Reduced from default 256MB
```

### 2. Gunicorn Workers Optimization

**Standard**: 2 workers + 2 threads per worker (hybrid model)
```bash
gunicorn --workers 2 --threads 2 --worker-class gthread
```

**Memory calculation**:
- Base: ~80MB
- Per worker: ~60-80MB
- Per thread: ~10-20MB
- Total: ~80 + (2 × 80) + (4 × 15) = 300MB max

**vs. Default (4 workers, no threads)**:
- Total: ~80 + (4 × 80) = 400MB

**Savings: ~100MB** while maintaining similar throughput!

### 3. Container Memory Limits

Prevents containers from consuming all available RAM:

```yaml
deploy:
  resources:
    limits:
      memory: 256M  # PostgreSQL
      memory: 512M  # Django Web
      memory: 256M  # Bot
      memory: 128M  # Nginx
```

### 4. Process Consolidation (Lite Config)

Combines Django + Bot into single container:
```bash
sh -c "python run_bot.py & gunicorn ..."
```

**Savings**: Eliminates container overhead (~50-100MB)

---

## 🚀 When to Use Which Configuration

### Use Standard (PostgreSQL) if:
- ✅ You have 1GB+ RAM
- ✅ Expecting >100 concurrent users
- ✅ Need database reliability and ACID guarantees
- ✅ Want to scale horizontally later
- ✅ Plan to add more services (Redis, Celery, etc.)

### Use Lite (SQLite) if:
- ✅ You have 512MB - 1GB RAM
- ✅ Small user base (<100 concurrent)
- ✅ Development/testing environment
- ✅ Budget-constrained (€4/mo vs €6/mo)
- ✅ Simple deployment without external database

---

## 📈 Scaling Path

### Current Setup → Growth Path

1. **Start**: Lite (SQLite) on 512MB VPS
   - Cost: €4/mo
   - Users: 0-50

2. **Upgrade**: Standard (PostgreSQL) on 1GB VPS
   - Cost: €6/mo
   - Users: 50-500
   - **Migration**: Export SQLite → Import PostgreSQL

3. **Scale**: Standard on 2GB+ VPS
   - Cost: €12/mo
   - Users: 500-5000
   - Increase workers: `--workers 4`

4. **Horizontal**: Multiple app servers + managed DB
   - Cost: €30+/mo
   - Users: 5000+
   - Use managed PostgreSQL (DigitalOcean, AWS RDS)

---

## 🛠️ Additional Optimizations

### 1. Add Swap Space

Essential for 1GB RAM setups:

```bash
sudo ./scripts/setup_swap.sh 1
```

**Benefits**:
- Prevents OOM kills
- Smoother memory pressure handling
- Acts as safety buffer

**Settings**:
- `vm.swappiness=10` - Use swap only when necessary
- `vm.vfs_cache_pressure=50` - Balance between cache and swap

### 2. Monitor Memory Usage

```bash
# Real-time container stats
docker stats

# Memory usage by container
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}"

# System memory
free -h

# Check OOM killer logs
dmesg | grep -i "out of memory"
```

### 3. Clean Up Docker

Prevents disk and memory bloat:

```bash
# Remove unused containers
docker container prune -f

# Remove unused images
docker image prune -a -f

# Remove build cache
docker builder prune -a -f
```

### 4. Optimize React Bundle Size

Already done in production build:

```javascript
// vite.config.js
build: {
  minify: 'esbuild',
  rollupOptions: {
    output: {
      manualChunks: {
        'react-vendor': ['react', 'react-dom'],
        'monaco': ['@monaco-editor/react'],
      }
    }
  }
}
```

---

## 🐛 Troubleshooting

### "Out of Memory" Errors

```bash
# Check OOM killer logs
dmesg | grep -i "killed process"

# If services are being killed:
1. Add/increase swap: sudo ./scripts/setup_swap.sh 2
2. Reduce gunicorn workers: --workers 1
3. Use Lite config instead of Standard
4. Upgrade VPS to 2GB RAM
```

### High Memory Usage

```bash
# Find memory hogs
docker stats --no-stream | sort -k4 -h

# Restart heavy containers
docker compose restart web

# Check for memory leaks in logs
docker compose logs web | grep -i memory
```

### Container Keeps Restarting

```bash
# Check restart reason
docker compose ps
docker compose logs --tail=50 app

# Often caused by:
- OOM (add swap)
- Crash on startup (check logs)
- Health check failing (check /health/ endpoint)
```

---

## 📚 Resources

- [Docker Memory Limits](https://docs.docker.com/config/containers/resource_constraints/)
- [PostgreSQL Memory Tuning](https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server)
- [Gunicorn Worker Optimization](https://docs.gunicorn.org/en/stable/design.html#how-many-workers)
- [Linux Swap Management](https://www.kernel.org/doc/Documentation/sysctl/vm.txt)

---

## 💰 Cost Comparison

### AlphaVPS (Budget Option)

| Plan | RAM | Storage | Config | Cost/mo | Users |
|------|-----|---------|--------|---------|-------|
| KVM 1GB | 1GB | 15GB SSD | Lite | $5 | <100 |
| KVM 2GB | 2GB | 30GB SSD | Standard | $7 | 100-500 |
| KVM 4GB | 4GB | 60GB SSD | Standard (4w) | $12 | 500+ |

### Hetzner (Premium Option)

| Plan | RAM | Storage | Config | Cost/mo | Users |
|------|-----|---------|--------|---------|-------|
| CX11 | 2GB | 20GB | Lite/Standard | €4 | <200 |
| CX22 | 4GB | 40GB | Standard | €6 | 200-1000 |
| CX32 | 8GB | 80GB | Standard (4w) | €12 | 1000+ |

### Which to Choose?

**Start with AlphaVPS if**:
- ✅ Budget is tight ($5/mo vs €4-6/mo)
- ✅ Learning/testing
- ✅ <100 users
- ✅ Can tolerate occasional slowness

**Choose Hetzner if**:
- ✅ Need reliability
- ✅ 100+ users
- ✅ Production-critical
- ✅ Want fast support

**Recommendation**:
- **Testing**: AlphaVPS KVM 1GB ($5) + Lite config
- **Small production**: AlphaVPS KVM 2GB ($7) + Standard config
- **Growth/serious**: Hetzner CX22 (€6) + Standard config
