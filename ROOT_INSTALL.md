# Root Installation Guide

This guide covers installing MyTube as the root user, which is common in server environments.

## 🆕 Recent Updates

- **JWT Authentication Fixed**: Resolved video upload failures (HTTP 422 errors)
- **Container Health Improved**: Fixed backend container health monitoring
- **Multi-Domain Support**: Enhanced CORS configuration for flexible deployment
- **Documentation Updated**: Comprehensive documentation updates with troubleshooting

## 🚨 Security Notice

Running as root is **not recommended** for production environments. However, it's sometimes necessary for initial server setup or in containerized environments.

## 🚀 Root Installation

### Quick Install
```bash
git clone https://github.com/ndoroe/my-tube.git
cd my-tube
chmod +x install.sh
./install.sh
```

When prompted about running as root, type `y` to continue.

### What Happens During Root Install

1. **Security Warning**: The script will warn about root usage and ask for confirmation
2. **Permission Management**: Attempts to set proper file ownership to non-root users
3. **Docker Access**: Uses root privileges to access Docker daemon directly
4. **File Creation**: Creates all necessary files and directories with appropriate permissions

## 🔧 Post-Installation Security

After installation, consider these security improvements:

### 1. Create Dedicated User
```bash
# Create mytube user
useradd -m -s /bin/bash mytube
usermod -aG docker mytube

# Transfer ownership
chown -R mytube:mytube /path/to/my-tube

# Switch to mytube user for operations
su - mytube
cd /path/to/my-tube
```

### 2. Run Services as Non-Root
```bash
# Stop services
docker-compose down

# Switch to non-root user
su - mytube
cd /path/to/my-tube

# Restart services
docker-compose up -d
```

### 3. Secure File Permissions
```bash
# Set restrictive permissions on sensitive files
chmod 600 .env
chmod 755 install.sh
chmod -R 755 uploads/
chmod -R 755 data/
```

## 🐳 Docker Considerations

### Running Docker as Root
- Docker daemon typically runs as root
- Container processes can run as non-root users
- MyTube containers are configured with non-root users where possible

### Container Security
```yaml
# Our containers use non-root users:
backend:
  user: mytube:mytube  # Non-root user inside container

frontend:
  user: nginx:nginx    # Nginx user inside container
```

## 🔒 Production Security Checklist

When running in production as root:

- [ ] Change all default passwords in `.env`
- [ ] Configure SSL/TLS certificates
- [ ] Set up firewall rules
- [ ] Enable Docker security features
- [ ] Regular security updates
- [ ] Monitor file permissions
- [ ] Use secrets management
- [ ] Enable audit logging

## 🌐 Server Environment Setup

### For VPS/Dedicated Servers
```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install MyTube
git clone https://github.com/ndoroe/my-tube.git
cd my-tube
./install.sh
```

### For Proxmox LXC (Root Required)
```bash
# In Proxmox LXC container (runs as root by default)
apt update && apt install -y docker.io docker-compose git curl
systemctl enable --now docker

# Install MyTube
git clone https://github.com/ndoroe/my-tube.git
cd my-tube
./install.sh
```

## 🛠 Root-Specific Commands

### System Management
```bash
# Check system resources
df -h
free -h
systemctl status docker

# Monitor Docker
docker system df
docker system prune -f

# Service management
systemctl start docker
systemctl enable docker
systemctl restart docker
```

### Log Management
```bash
# View system logs
journalctl -u docker
journalctl -f

# MyTube logs
docker-compose logs -f
docker-compose logs backend
docker-compose logs celery_worker
```

### Backup as Root
```bash
# Create backup script
cat > /root/backup-mytube.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/mytube"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T postgres pg_dump -U mytube_user mytube > \
  $BACKUP_DIR/mytube_db_$DATE.sql

# Backup uploads and config
tar -czf $BACKUP_DIR/mytube_files_$DATE.tar.gz uploads/ .env docker-compose.yml

# Keep only last 7 days
find $BACKUP_DIR -name "mytube_*" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /root/backup-mytube.sh

# Add to crontab
echo "0 2 * * * /root/backup-mytube.sh" | crontab -
```

## ⚠️ Common Root Issues

### Permission Problems
```bash
# Fix upload directory permissions
chown -R 1000:1000 uploads/
chmod -R 755 uploads/

# Fix Docker socket permissions
chmod 666 /var/run/docker.sock
```

### Docker Access Issues
```bash
# Start Docker daemon
systemctl start docker

# Check Docker status
systemctl status docker

# Test Docker access
docker run hello-world
```

### File Ownership Issues
```bash
# Check current ownership
ls -la

# Fix ownership for web server
chown -R www-data:www-data uploads/

# Fix ownership for specific user
chown -R mytube:mytube /path/to/my-tube
```

## 🔄 Migration from Root

To migrate from root to non-root user:

1. **Stop services**:
   ```bash
   docker-compose down
   ```

2. **Create user**:
   ```bash
   useradd -m -s /bin/bash mytube
   usermod -aG docker mytube
   ```

3. **Transfer ownership**:
   ```bash
   chown -R mytube:mytube /path/to/my-tube
   ```

4. **Switch user and restart**:
   ```bash
   su - mytube
   cd /path/to/my-tube
   docker-compose up -d
   ```

## 📞 Support

If you encounter issues with root installation:

1. Check the logs: `docker-compose logs`
2. Verify permissions: `ls -la`
3. Check Docker status: `systemctl status docker`
4. Review security settings
5. Create an issue on GitHub with details

## 🎯 Best Practices Summary

1. **Use root only when necessary** (initial setup, containers)
2. **Create dedicated users** for running services
3. **Set proper file permissions** (600 for secrets, 755 for directories)
4. **Enable security features** (firewall, SSL, monitoring)
5. **Regular updates** and security patches
6. **Backup regularly** with proper retention policies
7. **Monitor logs** for security events

Remember: Root access is powerful but requires careful security considerations!
