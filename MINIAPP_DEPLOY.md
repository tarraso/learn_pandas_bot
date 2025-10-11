# Miniapp Deployment Guide

Quick reference for deploying the React miniapp to the VPS.

## Quick Deploy

Deploy the latest miniapp changes with a single command:

```bash
./scripts/deploy_miniapp.sh
```

This script will:
1. Build the React app for production
2. Package the built files
3. Upload to VPS
4. Create automatic backup
5. Extract and deploy new files
6. Verify deployment

## Manual Deployment

If you prefer manual steps:

### 1. Build locally
```bash
cd webapp
npm run build
```

### 2. Package and upload
```bash
tar -czf /tmp/miniapp.tar.gz -C webapp/dist .
scp /tmp/miniapp.tar.gz root@94.72.140.27:/tmp/
```

### 3. Deploy on VPS
```bash
ssh root@94.72.140.27
cd /opt/pandas_bot/webapp/dist
rm -rf *
tar -xzf /tmp/miniapp.tar.gz
rm /tmp/miniapp.tar.gz
```

## Accessing the Miniapp

- **URL**: http://94.72.140.27/
- **Container**: `miniapp-nginx`

## Useful Commands

### Check deployment status
```bash
ssh root@94.72.140.27 "docker ps | grep miniapp"
```

### View nginx logs
```bash
ssh root@94.72.140.27 "docker logs miniapp-nginx"
ssh root@94.72.140.27 "docker logs -f miniapp-nginx"  # Follow logs
```

### Restart nginx (if needed)
```bash
ssh root@94.72.140.27 "docker restart miniapp-nginx"
```

### Check HTTP status
```bash
curl -I http://94.72.140.27/
```

## Rollback

Backups are automatically created before each deployment in `/opt/pandas_bot/backups/`.

To rollback:
```bash
ssh root@94.72.140.27
cd /opt/pandas_bot/backups
ls -lt | head  # Find latest backup
cp -r webapp-YYYYMMDD_HHMMSS/dist/* /opt/pandas_bot/webapp/dist/
```

## Configuration

### Change VPS host
Set environment variable before running script:
```bash
VPS_HOST=your.vps.ip ./scripts/deploy_miniapp.sh
```

Or edit the script directly:
```bash
VPS_HOST="your.vps.ip"
VPS_USER="your-user"
```

### Nginx Configuration

The nginx config is located at:
- **Host**: `/opt/pandas_bot/nginx/conf.d/miniapp.conf`
- **Container**: `/etc/nginx/conf.d/miniapp.conf`

After changing config, restart nginx:
```bash
ssh root@94.72.140.27 "docker restart miniapp-nginx"
```

## Troubleshooting

### Assets not loading (404)
Check the Vite base path in `webapp/vite.config.js`:
```javascript
base: '/',  // Should be '/' for standalone deployment
```

### Container not running
```bash
ssh root@94.72.140.27 "docker ps -a | grep miniapp"
ssh root@94.72.140.27 "docker logs miniapp-nginx"
```

Restart:
```bash
ssh root@94.72.140.27 "docker restart miniapp-nginx"
```

### Port 80 already in use
Check what's using port 80:
```bash
ssh root@94.72.140.27 "docker ps | grep ':80'"
```

Stop conflicting containers:
```bash
ssh root@94.72.140.27 "docker stop <container-name>"
```

## Development vs Production

- **Development**: `npm run dev` (runs on http://localhost:3000)
- **Production**: Deployed to VPS, served by nginx

The miniapp uses different base paths:
- Dev: `/` (served from Vite dev server)
- Prod: `/` (served from nginx static files)

## Adding SSL (Optional)

To add HTTPS support:

1. Install certbot on VPS
2. Generate certificates
3. Update nginx config to use SSL
4. Update miniapp URL to use https://

See `DEPLOY.md` for detailed SSL setup instructions.
