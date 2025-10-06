#!/bin/bash

# MyTube Installation Script
# This script sets up the MyTube video platform on your system

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root for security reasons."
        log_info "Please run as a regular user with sudo privileges."
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    log_info "Checking system requirements..."
    
    # Check OS
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        log_error "This script is designed for Linux systems only."
        exit 1
    fi
    
    # Check for required commands
    local required_commands=("docker" "docker-compose" "curl" "git")
    local missing_commands=()
    
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_commands+=("$cmd")
        fi
    done
    
    if [[ ${#missing_commands[@]} -gt 0 ]]; then
        log_error "Missing required commands: ${missing_commands[*]}"
        log_info "Please install the missing dependencies and run this script again."
        
        # Provide installation hints
        log_info "Installation hints:"
        for cmd in "${missing_commands[@]}"; do
            case $cmd in
                "docker")
                    log_info "  Docker: https://docs.docker.com/engine/install/"
                    ;;
                "docker-compose")
                    log_info "  Docker Compose: https://docs.docker.com/compose/install/"
                    ;;
                "curl")
                    log_info "  curl: sudo apt-get install curl (Ubuntu/Debian)"
                    ;;
                "git")
                    log_info "  git: sudo apt-get install git (Ubuntu/Debian)"
                    ;;
            esac
        done
        exit 1
    fi
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running or accessible."
        log_info "Please start Docker and ensure your user is in the docker group."
        log_info "Run: sudo usermod -aG docker \$USER && newgrp docker"
        exit 1
    fi
    
    log_success "All requirements satisfied."
}

# Generate secure random passwords
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

# Setup environment file
setup_environment() {
    log_info "Setting up environment configuration..."
    
    if [[ -f .env ]]; then
        log_warning ".env file already exists. Backing up to .env.backup"
        cp .env .env.backup
    fi
    
    # Copy example file
    cp .env.example .env
    
    # Generate secure passwords
    local flask_secret=$(generate_password)
    local jwt_secret=$(generate_password)
    local db_password=$(generate_password)
    
    # Update .env file with generated values
    sed -i "s/your-super-secret-flask-key-change-this/$flask_secret/" .env
    sed -i "s/your-super-secret-jwt-key-change-this/$jwt_secret/" .env
    sed -i "s/your-secure-database-password/$db_password/" .env
    
    log_success "Environment file configured with secure random passwords."
}

# Create necessary directories
setup_directories() {
    log_info "Creating necessary directories..."
    
    local directories=(
        "uploads/videos"
        "uploads/thumbnails" 
        "uploads/processed"
        "data/postgres"
        "data/redis"
        "logs"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        log_info "Created directory: $dir"
    done
    
    # Set proper permissions
    chmod 755 uploads
    chmod 755 data
    
    log_success "Directories created successfully."
}

# Build and start services
start_services() {
    log_info "Building and starting MyTube services..."
    
    # Pull latest images
    log_info "Pulling base Docker images..."
    docker-compose pull postgres redis nginx
    
    # Build custom images
    log_info "Building application images..."
    docker-compose build --no-cache
    
    # Start services
    log_info "Starting services..."
    docker-compose up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to start..."
    sleep 30
    
    # Check service health
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if docker-compose ps | grep -q "Up"; then
            log_success "Services are starting up..."
            break
        fi
        
        log_info "Attempt $attempt/$max_attempts: Waiting for services..."
        sleep 10
        ((attempt++))
    done
    
    if [[ $attempt -gt $max_attempts ]]; then
        log_error "Services failed to start within expected time."
        log_info "Check logs with: docker-compose logs"
        exit 1
    fi
}

# Initialize database
initialize_database() {
    log_info "Initializing database..."
    
    # Wait for database to be ready
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if docker-compose exec -T postgres pg_isready -U mytube_user -d mytube &> /dev/null; then
            log_success "Database is ready."
            break
        fi
        
        log_info "Attempt $attempt/$max_attempts: Waiting for database..."
        sleep 5
        ((attempt++))
    done
    
    if [[ $attempt -gt $max_attempts ]]; then
        log_error "Database failed to start within expected time."
        exit 1
    fi
    
    # Run database initialization
    log_info "Running database initialization script..."
    docker-compose exec backend python init_db.py
    
    log_success "Database initialized successfully."
}

# Display final information
show_completion_info() {
    log_success "🎉 MyTube installation completed successfully!"
    echo
    log_info "Access your MyTube instance:"
    log_info "  Web Interface: http://localhost"
    log_info "  API Endpoint:  http://localhost/api"
    echo
    log_info "Default admin credentials were set during database initialization."
    echo
    log_info "Useful commands:"
    log_info "  View logs:        docker-compose logs -f"
    log_info "  Stop services:    docker-compose down"
    log_info "  Start services:   docker-compose up -d"
    log_info "  Update services:  docker-compose pull && docker-compose up -d"
    echo
    log_info "Configuration files:"
    log_info "  Environment:      .env"
    log_info "  Docker Compose:   docker-compose.yml"
    echo
    log_warning "Important: Change default passwords and configure SSL for production use!"
    echo
    log_info "For support and documentation, visit: https://github.com/yourusername/my-tube"
}

# Cleanup function for errors
cleanup_on_error() {
    log_error "Installation failed. Cleaning up..."
    docker-compose down --remove-orphans 2>/dev/null || true
    log_info "Cleanup completed. Check the error messages above and try again."
}

# Main installation function
main() {
    echo "=================================="
    echo "   MyTube Installation Script"
    echo "=================================="
    echo
    
    # Set trap for cleanup on error
    trap cleanup_on_error ERR
    
    # Run installation steps
    check_root
    check_requirements
    setup_environment
    setup_directories
    start_services
    initialize_database
    show_completion_info
    
    log_success "Installation completed successfully! 🚀"
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "MyTube Installation Script"
        echo
        echo "Usage: $0 [options]"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --check        Check system requirements only"
        echo "  --uninstall    Uninstall MyTube (removes containers and data)"
        echo
        exit 0
        ;;
    --check)
        check_requirements
        log_success "System requirements check passed!"
        exit 0
        ;;
    --uninstall)
        log_warning "This will remove all MyTube containers and data!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Uninstalling MyTube..."
            docker-compose down --volumes --remove-orphans
            docker system prune -f
            rm -rf uploads data logs
            log_success "MyTube uninstalled successfully."
        else
            log_info "Uninstall cancelled."
        fi
        exit 0
        ;;
    "")
        # No arguments, run main installation
        main
        ;;
    *)
        log_error "Unknown option: $1"
        log_info "Use --help for usage information."
        exit 1
        ;;
esac
