# MyTube Deployment Guide

This guide covers deploying MyTube on various platforms, with a focus on Proxmox and self-hosting scenarios.

## Recent Updates

- **JWT Authentication**: Fixed JWT token identity format for improved compatibility
- **CORS Configuration**: Enhanced support for multi-domain deployments
- **Health Checks**: Improved container health monitoring
- **Upload Reliability**: Resolved HTTP 422 upload errors

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Proxmox Deployment](#proxmox-deployment)
4. [Production Configuration](#production-configuration)
5. [SSL/TLS Setup](#ssltls-setup)
6. [Backup and Maintenance](#backup-and-maintenance)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **OS**: Ubuntu 20.04+ or Debian 11+ (recommended)
- **CPU**: 2+ cores (4+ recommended for video processing)
- **RAM**: 4GB minimum (8GB+ recommended)
- **Storage**: 50GB+ available space
- **Network**: Internet connection for initial setup

### Required Software

- Docker 20.10+
- Docker Compose 2.0+
- Git
- curl

### Hardware Recommendations

For optimal video processing performance:

- **CPU**: Modern multi-core processor with hardware video encoding support
- **RAM**: 8GB+ (more RAM = faster video processing)
- **Storage**: SSD recommended for database and application files
- **Network**: Gigabit ethernet for large video uploads

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/my-tube.git
cd my-tube
```

### 2. Run Installation Script

```bash
chmod +x install.sh
./install.sh
```

The installation script will:
- Check system requirements
- Generate secure passwords
- Create necessary directories
- Build and start all services
- Initialize the database
- Create admin user account

### 3. Access Your Instance

- **Web Interface**: http://localhost
- **API**: http://localhost/api

## Proxmox Deployment

### Option 1: LXC Container (Recommended)

1. **Create LXC Container**:
   ```bash
   # In Proxmox web interface:
   # - Create new LXC container
   # - Template: Ubuntu 22.04
   # - CPU: 4 cores
   # - Memory: 8192 MB
   # - Storage: 100 GB
   # - Network: Bridge to your network
   ```

2. **Configure Container**:
   ```bash
   # Enable nesting for Docker
   echo "lxc.apparmor.profile: unconfined" >> /etc/pve/lxc/CONTAINER_ID.conf
   echo "lxc.cgroup2.devices.allow: a" >> /etc/pve/lxc/CONTAINER_ID.conf
   echo "lxc.cap.drop:" >> /etc/pve/lxc/CONTAINER_ID.conf
   echo "lxc.mount.auto: proc:rw sys:rw" >> /etc/pve/lxc/CONTAINER_ID.conf
   ```

3. **Install Dependencies**:
   ```bash
   # Inside the container
   apt update && apt upgrade -y
   apt install -y docker.io docker-compose git curl
   systemctl enable --now docker
   ```

4. **Deploy MyTube**:
   ```bash
   git clone https://github.com/yourusername/my-tube.git
   cd my-tube
   ./install.sh
   ```

### Option 2: Virtual Machine

1. **Create VM**:
   - OS: Ubuntu Server 22.04 LTS
   - CPU: 4 cores
   - RAM: 8GB
   - Disk: 100GB
   - Network: Bridged

2. **Follow standard installation process**

## Production Configuration

### Environment Variables

Create a production `.env` file:

```bash
# Copy and modify the example
cp .env.example .env

# Edit with your production values
nano .env
```

Key production settings:

```env
# Security
FLASK_ENV=production
FLASK_SECRET_KEY=your-super-secure-secret-key
JWT_SECRET_KEY=your-super-secure-jwt-key

# Database
POSTGRES_PASSWORD=your-secure-database-password

# Multi-Domain Configuration (NEW)
ALLOWED_HOSTS=yourdomain.com,192.168.1.100,localhost
CORS_ORIGINS=https://yourdomain.com,http://192.168.1.100,http://localhost

# Upload Configuration
MAX_CONTENT_LENGTH=2147483648  # 2GB
UPLOAD_FOLDER=/app/uploads

# Domain
DOMAIN=your-domain.com
VITE_API_URL=https://your-domain.com/api

# CORS
CORS_ORIGINS=https://your-domain.com

# File Upload
MAX_CONTENT_LENGTH=5368709120  # 5GB
```

### Resource Limits

Configure Docker resource limits in `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
  
  celery_worker:
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
```

### Database Optimization

For production PostgreSQL:

```yaml
postgres:
  environment:
    POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
  command: >
    postgres
    -c shared_buffers=256MB
    -c effective_cache_size=1GB
    -c maintenance_work_mem=64MB
    -c checkpoint_completion_target=0.9
    -c wal_buffers=16MB
    -c default_statistics_target=100
```

## SSL/TLS Setup

### Option 1: Let's Encrypt (Recommended)

1. **Install Certbot**:
   ```bash
   apt install -y certbot python3-certbot-nginx
   ```

2. **Obtain Certificate**:
   ```bash
   certbot certonly --standalone -d your-domain.com
   ```

3. **Configure Nginx**:
   ```bash
   # Update docker/nginx/default.conf
   # Uncomment and configure the HTTPS server block
   ```

4. **Auto-renewal**:
   ```bash
   # Add to crontab
   0 12 * * * /usr/bin/certbot renew --quiet
   ```

### Option 2: Self-Signed Certificate

```bash
# Generate certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem

# Update docker-compose.yml to mount certificates
```

## Backup and Maintenance

### Database Backup

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T postgres pg_dump -U mytube_user mytube > \
  $BACKUP_DIR/mytube_db_$DATE.sql

# Backup uploads
tar -czf $BACKUP_DIR/mytube_uploads_$DATE.tar.gz uploads/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "mytube_*" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x backup.sh

# Add to crontab for daily backups
echo "0 2 * * * /path/to/backup.sh" | crontab -
```

### System Updates

```bash
# Update script
cat > update.sh << 'EOF'
#!/bin/bash
cd /path/to/my-tube

# Pull latest changes
git pull

# Update containers
docker-compose pull
docker-compose up -d --build

# Clean up old images
docker system prune -f

echo "Update completed"
EOF

chmod +x update.sh
```

### Log Rotation

```bash
# Configure log rotation
cat > /etc/logrotate.d/mytube << 'EOF'
/path/to/my-tube/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose restart nginx
    endscript
}
EOF
```

## Monitoring

### Health Checks

```bash
# Health check script
cat > health-check.sh << 'EOF'
#!/bin/bash

# Check if services are running
if ! docker-compose ps | grep -q "Up"; then
    echo "ERROR: Some services are down"
    exit 1
fi

# Check web interface
if ! curl -f http://localhost/health > /dev/null 2>&1; then
    echo "ERROR: Web interface not responding"
    exit 1
fi

# Check API
if ! curl -f http://localhost/api/auth/me > /dev/null 2>&1; then
    echo "ERROR: API not responding"
    exit 1
fi

echo "All services healthy"
EOF

chmod +x health-check.sh
```

### Resource Monitoring

```bash
# Monitor disk usage
df -h
du -sh uploads/

# Monitor Docker resources
docker stats

# Monitor logs
docker-compose logs -f --tail=100
```

## Troubleshooting

### Recently Fixed Issues

1. **Video Upload Failures (HTTP 422)**:
   - **Status**: ✅ FIXED in latest version
   - **Issue**: JWT token identity format incompatibility
   - **Solution**: JWT tokens now use string identities instead of integers
   - **Action**: Update to latest version and rebuild containers

2. **Backend Container Unhealthy**:
   - **Status**: ✅ FIXED in latest version  
   - **Issue**: Health check using authenticated endpoint
   - **Solution**: Health check now uses `/api/categories/` (unauthenticated)
   - **Action**: Update docker-compose.yml and restart backend

3. **CORS Errors on Multi-Domain Setup**:
   - **Status**: ✅ IMPROVED in latest version
   - **Issue**: CORS origins not properly configured
   - **Solution**: Enhanced CORS configuration in nginx and backend
   - **Action**: Configure `CORS_ORIGINS` and `ALLOWED_HOSTS` in `.env`

### Common Issues

1. **Services won't start**:
   ```bash
   # Check logs
   docker-compose logs
   
   # Check system resources
   free -h
   df -h
   
   # Restart services
   docker-compose down
   docker-compose up -d
   ```

2. **Video processing fails**:
   ```bash
   # Check FFmpeg installation
   docker-compose exec backend ffmpeg -version
   
   # Check worker logs
   docker-compose logs celery_worker
   
   # Restart worker
   docker-compose restart celery_worker
   ```

3. **Database connection issues**:
   ```bash
   # Check database status
   docker-compose exec postgres pg_isready -U mytube_user
   
   # Check database logs
   docker-compose logs postgres
   
   # Reset database (WARNING: destroys data)
   docker-compose down -v
   docker-compose up -d
   ```

4. **Permission issues**:
   ```bash
   # Fix upload directory permissions
   sudo chown -R 1000:1000 uploads/
   chmod -R 755 uploads/
   ```

5. **Authentication Issues**:
   ```bash
   # Clear browser cache and localStorage
   # Re-login to get new JWT token format
   
   # Check JWT configuration
   grep JWT_SECRET_KEY .env
   
   # Verify backend is using string identities
   docker-compose logs backend | grep "identity"
   ```

5. **Out of disk space**:
   ```bash
   # Clean up Docker
   docker system prune -a
   
   # Clean up old videos (if needed)
   find uploads/ -name "*.mp4" -mtime +30 -delete
   ```

### Performance Optimization

1. **Video Processing**:
   - Increase Celery worker concurrency
   - Use hardware-accelerated encoding
   - Optimize FFmpeg settings

2. **Database**:
   - Tune PostgreSQL configuration
   - Add database indexes
   - Regular VACUUM and ANALYZE

3. **Storage**:
   - Use SSD for database
   - Separate storage for videos
   - Implement CDN for video delivery

### Getting Help

1. Check the logs: `docker-compose logs`
2. Review this documentation
3. Check GitHub issues
4. Create a new issue with:
   - System information
   - Error logs
   - Steps to reproduce

## Security Considerations

1. **Change default passwords**
2. **Enable firewall**
3. **Regular security updates**
4. **Use HTTPS in production**
5. **Limit file upload sizes**
6. **Regular backups**
7. **Monitor access logs**

For additional security hardening, consider:
- Fail2ban for brute force protection
- Regular security audits
- Network segmentation
- Access logging and monitoring
