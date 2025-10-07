# MyTube Troubleshooting Guide

This comprehensive guide covers solutions to common issues you might encounter with MyTube.

## 🔍 Recently Fixed Issues

### ✅ Video Upload Failures (HTTP 422) - RESOLVED
**Issue**: Video uploads failing with HTTP 422 "Unprocessable Entity" errors
**Root Cause**: JWT token identity format incompatibility (integer vs string)
**Status**: Fixed in version 1.1.0

**Solution Applied**:
- Modified JWT token creation to use string identities: `str(user.id)`
- Updated all `get_jwt_identity()` usage to convert back to integer for database queries
- Fixed authentication across all protected endpoints

**Files Modified**:
- `backend/app/routes/auth.py`
- `backend/app/routes/videos.py`
- `backend/app/routes/users.py`
- `backend/app/routes/categories.py`

### ✅ Backend Container Unhealthy - RESOLVED
**Issue**: Backend containers showing as "unhealthy" in Docker
**Root Cause**: Health check using authenticated endpoint `/api/auth/me`
**Status**: Fixed in version 1.1.0

**Solution Applied**:
- Changed health check endpoint to `/api/categories/` (unauthenticated)
- Updated `docker-compose.yml` configuration

**File Modified**:
- `docker-compose.yml`

### ✅ CORS Errors on Multi-Domain Setup - IMPROVED
**Issue**: Cross-origin requests blocked when accessing from different domains
**Root Cause**: Limited CORS configuration
**Status**: Enhanced in version 1.1.0

**Solution Applied**:
- Added configurable `CORS_ORIGINS` environment variable
- Enhanced nginx CORS handling
- Added `ALLOWED_HOSTS` configuration

**Files Modified**:
- `docker/nginx/default.conf`
- `backend/app/__init__.py`
- `.env` configuration

## 🛠 Current Known Issues

### Celery Worker Unhealthy
**Issue**: Celery worker container may show as unhealthy
**Impact**: Background video processing may be affected
**Temporary Workaround**: Monitor processing manually
**Status**: Under investigation

## 🔧 Common Issues & Solutions

### Authentication Problems

#### "Subject must be a string" Error
```bash
# This error is fixed in the latest version
# If you still see it:

# 1. Update to latest version
git pull origin main

# 2. Rebuild containers
docker-compose build backend
docker-compose restart backend

# 3. Clear browser localStorage
# In browser console: localStorage.clear()

# 4. Login again to get new token format
```

#### JWT Token Expired
```bash
# Symptoms: 401 Unauthorized errors
# Solution: Re-login to refresh token

curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

### Upload Issues

#### File Upload Fails
```bash
# Check file format
echo "Supported formats: MP4, AVI, MOV, MKV, WebM, FLV, M4V, 3GP, OGV"

# Check file size (default limit: 2GB)
ls -lh your_video_file.mp4

# Check authentication
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5000/api/auth/me

# Test upload with curl
curl -X POST http://localhost:5000/api/videos/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "video=@test_video.mp4" \
  -F "title=Test Video" \
  -F "category_id=1"
```

#### Upload Directory Permissions
```bash
# Fix upload directory permissions
sudo chown -R 1000:1000 uploads/
chmod -R 755 uploads/

# Or for Docker user
docker-compose exec backend chown -R mytube:mytube /app/uploads
```

### Container Issues

#### Services Won't Start
```bash
# Check Docker status
systemctl status docker

# Check available resources
free -h
df -h

# Check container logs
docker-compose logs

# Restart all services
docker-compose down
docker-compose up -d

# Force rebuild if needed
docker-compose build --no-cache
docker-compose up -d
```

#### Database Connection Issues
```bash
# Test database connection
docker-compose exec postgres pg_isready -U mytube_user -d mytube

# Check database logs
docker-compose logs postgres

# Connect to database manually
docker-compose exec postgres psql -U mytube_user -d mytube

# Reset database (WARNING: destroys all data)
docker-compose down -v
docker-compose up -d
```

### Network Issues

#### CORS Errors
```bash
# Configure CORS origins in .env
echo "CORS_ORIGINS=http://localhost:3000,https://yourdomain.com" >> .env

# Configure allowed hosts
echo "ALLOWED_HOSTS=localhost,yourdomain.com,192.168.1.100" >> .env

# Restart containers
docker-compose restart

# Test CORS
curl -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -X OPTIONS http://localhost:5000/api/videos
```

#### Can't Access Web Interface
```bash
# Check if nginx is running
docker-compose ps nginx

# Check nginx logs
docker-compose logs nginx

# Test direct backend access
curl http://localhost:5000/api/categories

# Check port bindings
docker-compose ps
```

### Performance Issues

#### Slow Video Processing
```bash
# Check Celery worker status
docker-compose logs celery_worker

# Monitor system resources
docker stats

# Check available disk space
df -h

# Restart worker
docker-compose restart celery_worker
```

#### High Memory Usage
```bash
# Check memory usage by container
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Restart resource-heavy containers
docker-compose restart backend celery_worker

# Adjust container memory limits in docker-compose.yml
```

## 🔍 Diagnostic Commands

### System Health Check
```bash
#!/bin/bash
echo "=== MyTube System Health Check ==="

echo "1. Container Status:"
docker-compose ps

echo -e "\n2. Service Health:"
curl -s http://localhost/api/categories | head -c 100

echo -e "\n3. Database Status:"
docker-compose exec postgres pg_isready -U mytube_user -d mytube

echo -e "\n4. Storage Usage:"
df -h uploads/

echo -e "\n5. Memory Usage:"
free -h

echo -e "\n6. Recent Errors:"
docker-compose logs --since=1h | grep -i error | tail -5
```

### Log Analysis
```bash
# Check recent backend errors
docker-compose logs backend --since=1h | grep -i error

# Check authentication issues
docker-compose logs backend | grep -i "jwt\|auth\|token"

# Check upload issues
docker-compose logs backend | grep -i "upload\|422\|400"

# Check all recent errors
docker-compose logs --since=1h | grep -E "(error|Error|ERROR|fail|Fail|FAIL)"
```

## 📞 Getting Help

### Before Seeking Help

1. **Check this troubleshooting guide**
2. **Review recent logs**: `docker-compose logs --since=1h`
3. **Verify system requirements**: Docker, resources, etc.
4. **Try basic fixes**: restart containers, check permissions

### Information to Include

When reporting issues, include:

```bash
# System information
echo "OS: $(uname -a)"
echo "Docker: $(docker --version)"
echo "Docker Compose: $(docker-compose --version)"

# MyTube version
git log -1 --oneline

# Container status
docker-compose ps

# Recent logs
docker-compose logs --since=1h --tail=50
```

### Resources

- **Documentation**: `./docs/`
- **API Reference**: `./docs/API.md`
- **Deployment Guide**: `./docs/DEPLOYMENT.md`
- **Changelog**: `./CHANGELOG.md`

## 🔄 Update Procedure

To get the latest fixes:

```bash
# Backup your data first
docker-compose exec postgres pg_dump -U mytube_user mytube > backup.sql

# Update code
git pull origin main

# Rebuild containers with latest fixes
docker-compose build --no-cache

# Restart all services
docker-compose down
docker-compose up -d

# Verify everything is working
docker-compose ps
curl http://localhost/api/categories
```

---

**Last Updated**: October 6, 2025  
**Version**: 1.1.0