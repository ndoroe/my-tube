# MyTube Quick Start Guide

Get your MyTube video platform running in minutes!

## 🚀 One-Command Installation

```bash
git clone https://github.com/ndoroe/my-tube.git
cd my-tube
chmod +x install.sh
./install.sh
```

That's it! The installation script will handle everything automatically.

## 📋 What the Installation Does

1. **System Check**: Verifies Docker, Docker Compose, and other requirements
2. **Security Setup**: Generates secure random passwords for all services
3. **Environment Configuration**: Creates `.env` file with secure defaults
4. **Service Deployment**: Builds and starts all Docker containers
5. **Database Setup**: Initializes PostgreSQL with proper schema
6. **Admin Account**: Prompts you to create the system administrator

## 🌐 Access Your Platform

After installation completes:

- **Web Interface**: http://localhost
- **Admin Login**: Use the credentials you created during setup
- **API Endpoint**: http://localhost/api

## 🔧 First Steps

### 1. Login as Admin
- Navigate to http://localhost
- Click "Login" and use your admin credentials
- You'll see the admin dashboard

### 2. Create User Accounts
- Go to Admin → Users
- Click "Create User" to add new accounts
- Only admins can create users (security feature)

### 3. Set Up Categories
- Navigate to Categories
- Create categories like "Education", "Entertainment", etc.
- Choose whether to make them shared (visible to all users)

### 4. Upload Your First Video
- Click "Upload" in the navigation
- Drag and drop a video file or click to browse
- Add title, description, category, and tags
- Click "Upload Video"

### 5. Watch Processing
- Videos are processed automatically in the background
- Multiple resolutions are generated (360p, 720p, 1080p, 4K)
- You can monitor progress on the video page

## 📱 Using the Platform

### For Viewers (No Account Needed)
- Browse all public videos on the homepage
- Search videos by title, description, or tags
- Filter by category or uploader
- Watch videos with adaptive quality
- Preview videos before clicking

### For Users (Account Required)
- Upload videos in any format
- Download videos you have access to
- Organize content with categories and tags
- Edit video metadata
- View detailed statistics

### For Admins
- Manage all user accounts
- Control category sharing permissions
- Monitor system resources and usage
- Access advanced admin tools

## 🔒 Security Features

- **Admin-Only Registration**: Only admins can create accounts
- **Role-Based Access**: Separate permissions for users and admins
- **Secure Authentication**: JWT tokens with automatic refresh
- **File Validation**: Comprehensive upload security checks
- **Rate Limiting**: Protection against abuse

## 📊 System Requirements

### Minimum
- 2 CPU cores
- 4GB RAM
- 50GB storage
- Docker & Docker Compose

### Recommended
- 4+ CPU cores
- 8GB+ RAM
- 500GB+ SSD storage
- Hardware video encoding support

## 🐳 Docker Services

Your MyTube installation includes:

- **Frontend**: React app (port 3000 → 80)
- **Backend**: Flask API (port 5000)
- **Database**: PostgreSQL (port 5432)
- **Cache**: Redis (port 6379)
- **Worker**: Celery for video processing
- **Proxy**: Nginx reverse proxy (port 80)

## 🛠 Management Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Start services
docker-compose up -d

# Update to latest version
git pull
docker-compose pull
docker-compose up -d --build

# Backup database
docker-compose exec postgres pg_dump -U mytube_user mytube > backup.sql

# Check system status
./install.sh --check
```

## 🔧 Configuration

### Environment Variables
Edit `.env` file to customize:

```env
# Change maximum upload size (in bytes)
MAX_CONTENT_LENGTH=5368709120  # 5GB

# Configure domain for production
DOMAIN=your-domain.com
VITE_API_URL=https://your-domain.com/api
```

### Video Processing
Modify `backend/config.py` to adjust:
- Video resolutions generated
- Processing quality settings
- Thumbnail generation timing

## 🌐 Production Deployment

### For Proxmox LXC Container

1. **Create Container**:
   - Template: Ubuntu 22.04
   - CPU: 4 cores
   - Memory: 8GB
   - Storage: 100GB

2. **Enable Docker Support**:
   ```bash
   # Add to container config
   echo "lxc.apparmor.profile: unconfined" >> /etc/pve/lxc/CONTAINER_ID.conf
   echo "lxc.cgroup2.devices.allow: a" >> /etc/pve/lxc/CONTAINER_ID.conf
   ```

3. **Install and Deploy**:
   ```bash
   # Inside container
   apt update && apt install -y docker.io docker-compose git
   git clone https://github.com/ndoroe/my-tube.git
   cd my-tube
   ./install.sh
   ```

### SSL/HTTPS Setup

1. **Get SSL Certificate**:
   ```bash
   # Using Let's Encrypt
   apt install certbot
   certbot certonly --standalone -d your-domain.com
   ```

2. **Configure Nginx**:
   - Edit `docker/nginx/default.conf`
   - Uncomment HTTPS server block
   - Update certificate paths

3. **Update Environment**:
   ```env
   DOMAIN=your-domain.com
   VITE_API_URL=https://your-domain.com/api
   ```

## 🆘 Troubleshooting

### Services Won't Start
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

### Video Processing Issues
```bash
# Check worker logs
docker-compose logs celery_worker

# Restart worker
docker-compose restart celery_worker

# Check FFmpeg
docker-compose exec backend ffmpeg -version
```

### Database Connection Issues
```bash
# Check database
docker-compose exec postgres pg_isready -U mytube_user

# Reset database (WARNING: destroys data)
docker-compose down -v
docker-compose up -d
```

### Permission Issues
```bash
# Fix upload permissions
sudo chown -R 1000:1000 uploads/
chmod -R 755 uploads/
```

## 📚 Additional Resources

- **[Full Documentation](docs/)**: Complete guides and API reference
- **[Deployment Guide](docs/DEPLOYMENT.md)**: Detailed deployment instructions
- **[API Documentation](docs/API.md)**: REST API reference
- **[Testing Guide](docs/TESTING.md)**: Testing procedures

## 🤝 Support

- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share tips
- **Documentation**: Check the docs/ directory for detailed guides

## 🎉 You're Ready!

Your MyTube platform is now running and ready to use. Start uploading videos and building your content library!

**Default Access**:
- URL: http://localhost
- Admin: Use credentials created during setup
- Users: Create via admin panel

Enjoy your self-hosted video platform! 🎬
