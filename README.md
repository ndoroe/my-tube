# MyTube - Self-Hosted Video Platform

A modern, self-hosted video platform similar to YouTube, built with Flask and React. Perfect for organizations, content creators, or anyone who wants complete control over their video content.

![MyTube Logo](https://via.placeholder.com/800x200/2563eb/ffffff?text=MyTube+-+Self-Hosted+Video+Platform)

## ✨ Features

### 🎥 Video Management
- **Multi-format Support**: Upload videos in MP4, AVI, MOV, MKV, WebM, and more
- **Automatic Transcoding**: Generate multiple resolutions (360p, 720p, 1080p, 4K) for optimal playback
- **Smart Thumbnails**: Automatic thumbnail generation with custom timing
- **Video Preview**: Hover previews and detailed video information
- **Download Support**: Direct video downloads for authenticated users

### 👥 User Management
- **Role-Based Access**: Admin and user roles with granular permissions
- **Secure Authentication**: JWT-based authentication with refresh tokens
- **Admin Controls**: User creation, activation, and permission management
- **Admin-Only Registration**: Controlled user creation for security

### 📁 Content Organization
- **Categories**: Organize videos with shared or private categories
- **Tags**: Flexible tagging system for better discoverability
- **Search**: Full-text search across titles, descriptions, and tags
- **Filtering**: Advanced filtering by category, uploader, date, and more

### 🔒 Security & Privacy
- **Private Content**: User-specific private categories and videos
- **Secure File Handling**: Validated uploads with comprehensive security checks
- **Permission Controls**: Granular access control for all resources
- **Public Viewing**: Anyone can browse and watch videos without authentication

### 🚀 Performance & Scalability
- **Async Processing**: Background video processing with Celery
- **Multi-Resolution Streaming**: Adaptive bitrate for all devices
- **Caching**: Redis-based caching for improved performance
- **Responsive Design**: Mobile-first, responsive web interface

## 🏗 Technology Stack

### Backend
- **Framework**: Flask (Python) with SQLAlchemy ORM
- **Database**: PostgreSQL for production-grade performance
- **Authentication**: JWT with role-based access control (Fixed string identity compatibility)
- **Video Processing**: FFmpeg for transcoding and thumbnail generation
- **Background Tasks**: Celery with Redis for async processing
- **CORS Support**: Configurable CORS origins for multi-domain deployment

### Frontend
- **Framework**: React with modern hooks and functional components
- **UI Library**: Tailwind CSS with shadcn/ui components
- **Video Player**: Video.js for cross-browser video playback
- **State Management**: React Context API for authentication state
- **File Upload**: Drag-and-drop interface with progress indicators

### Infrastructure
- **Containerization**: Docker and Docker Compose for easy deployment
- **Web Server**: Nginx reverse proxy for production
- **Database**: PostgreSQL container with optimized configuration
- **Cache/Queue**: Redis for caching and task queues

## 🚀 Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Git
- 4GB+ RAM
- 50GB+ storage space

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/my-tube.git
   cd my-tube
   ```

2. **Run the installation script**:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. **Access your MyTube instance**:
   - Web Interface: http://localhost
   - API Documentation: http://localhost/api

The installation script will:
- Check system requirements
- Generate secure passwords
- Build and start all services
- Initialize the database
- Create your admin account

## � Configuration

### Allowed Hosts Configuration

MyTube supports multiple allowed hosts for deployment flexibility:

```bash
# In .env file
ALLOWED_HOSTS=my-tube,192.168.101.112,videos.edron.duckdns.org
CORS_ORIGINS=http://my-tube,http://192.168.101.112,https://videos.edron.duckdns.org
```

This enables:
- Local development (`my-tube`)
- LAN access (`192.168.101.112`)
- External domain access (`videos.edron.duckdns.org`)

### Environment Variables

Key configuration options:

```bash
# Database Configuration
POSTGRES_DB=mytube
POSTGRES_USER=mytube_user
POSTGRES_PASSWORD=secure_password

# JWT Configuration
JWT_SECRET_KEY=your_secure_jwt_secret

# Upload Configuration
UPLOAD_FOLDER=/app/uploads
MAX_CONTENT_LENGTH=2147483648  # 2GB

# CORS Configuration
CORS_ORIGINS=http://localhost,http://127.0.0.1
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 🚨 Troubleshooting

### Common Issues

**Video Upload Fails (HTTP 422)**
- Fixed: JWT authentication now properly handles string identities
- Ensure you're logged in with valid credentials
- Check file format is supported (MP4, AVI, MOV, MKV, WebM, etc.)

**Backend Container Unhealthy**
- Fixed: Health check now uses unauthenticated endpoint
- Check if containers are running: `docker compose ps`
- View logs: `docker compose logs backend`

**CORS Errors**
- Configure `CORS_ORIGINS` in `.env` with your domain(s)
- Restart containers after configuration changes

**Authentication Issues**
- JWT tokens now use string identities for compatibility
- Clear browser cache/localStorage if experiencing login issues

## �📁 Project Structure

```
my-tube/
├── backend/                    # Flask API server
│   ├── app/
│   │   ├── models/            # Database models
│   │   ├── routes/            # API endpoints
│   │   ├── services/          # Business logic
│   │   └── utils/             # Utility functions
│   ├── requirements.txt       # Python dependencies
│   ├── run.py                # Application entry point
│   ├── init_db.py            # Database initialization
│   └── Dockerfile            # Backend container config
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/            # Page components
│   │   ├── contexts/         # React contexts
│   │   └── lib/              # Utilities and API client
│   ├── package.json          # Node.js dependencies
│   └── Dockerfile            # Frontend container config
├── docker/                    # Docker configuration
│   ├── nginx/                # Nginx configuration
│   └── postgres/             # Database initialization
├── docs/                      # Documentation
│   ├── DEPLOYMENT.md         # Deployment guide
│   ├── API.md               # API documentation
│   └── TESTING.md           # Testing guide
├── docker-compose.yml        # Multi-container setup
├── install.sh               # Installation script
├── .env.example             # Environment template
└── README.md               # This file
```

## ⚙️ Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# Security
FLASK_SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Database
POSTGRES_DB=mytube
POSTGRES_USER=mytube_user
POSTGRES_PASSWORD=your-secure-password

# File Upload
MAX_CONTENT_LENGTH=2147483648  # 2GB max file size

# Domain (for production)
DOMAIN=your-domain.com
VITE_API_URL=https://your-domain.com/api
```

### Video Processing

Configure video resolutions and quality settings in the backend configuration.

## 🐳 Docker Services

MyTube consists of several Docker services:

- **Frontend**: React application served by Nginx
- **Backend**: Flask API server with Gunicorn
- **Database**: PostgreSQL for data storage
- **Cache**: Redis for caching and task queues
- **Worker**: Celery worker for video processing
- **Proxy**: Nginx reverse proxy and load balancer

## 📖 Documentation

- **[Quick Start Guide](QUICK_START.md)** - Get up and running in minutes
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Complete deployment instructions for Proxmox and other platforms
- **[API Documentation](docs/API.md)** - REST API reference with examples
- **[Testing Guide](docs/TESTING.md)** - Testing procedures and automation
- **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Solutions to common issues
- **[Changelog](CHANGELOG.md)** - Version history and updates

## 🔧 Usage

### Admin Functions
- Create and manage user accounts
- Configure category sharing permissions
- Monitor system usage and storage
- Manage video processing and system health

### User Functions
- Upload videos in any supported format
- Organize videos with categories and tags
- Download videos (authenticated users only)
- Preview videos before full playback
- Search and filter video content

### Public Access
- Browse and watch all public videos
- Search through available content
- View video details and metadata
- No registration required for viewing

## 🛠 Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

### Frontend Development
```bash
cd frontend
pnpm install
pnpm dev
```

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest tests/ -v

# Frontend tests
cd frontend
pnpm test
```

## 🚀 Deployment

### For Proxmox

1. Create an LXC container or VM
2. Install Docker and Docker Compose
3. Clone the repository and run the installation script
4. Configure networking and SSL certificates

See the [Deployment Guide](docs/DEPLOYMENT.md) for detailed instructions.

### For Production

1. Configure SSL certificates
2. Set up proper domain names
3. Configure backup procedures
4. Set up monitoring and logging
5. Optimize for your expected load

## 🔐 Security Features

- **JWT Authentication** with secure token rotation
- **Role-based Access Control** (RBAC)
- **Input Validation** and sanitization
- **File Type Validation** with magic number checking
- **Rate Limiting** on API endpoints
- **CORS Protection** for cross-origin requests
- **SQL Injection Protection** via ORM
- **XSS Prevention** with content security policies

## 📊 System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 50GB
- **Network**: 10 Mbps upload

### Recommended for Production
- **CPU**: 4+ cores with hardware video encoding
- **RAM**: 8GB+
- **Storage**: 500GB+ SSD
- **Network**: 100 Mbps+ with low latency

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FFmpeg** - Video processing engine
- **Video.js** - HTML5 video player
- **React** - Frontend framework
- **Flask** - Backend framework
- **PostgreSQL** - Database system
- **Docker** - Containerization platform

## 📞 Support

- **Documentation**: Check our [docs](docs/) directory
- **Issues**: Report bugs on [GitHub Issues](https://github.com/yourusername/my-tube/issues)
- **Questions**: Ask questions in [GitHub Discussions](https://github.com/yourusername/my-tube/discussions)

## 🗺 Roadmap

### Upcoming Features
- [ ] Live streaming support
- [ ] Video comments and ratings
- [ ] Playlist management
- [ ] Advanced analytics dashboard
- [ ] Subtitle support (SRT, VTT)
- [ ] Mobile app (React Native)

---

**Made with ❤️ for the self-hosting community**

*MyTube gives you complete control over your video content while providing a modern, user-friendly experience similar to popular video platforms.*
