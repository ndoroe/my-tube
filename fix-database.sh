#!/bin/bash

# Fix database credential issues for MyTube

echo "==================================="
echo "   MyTube Database Fix Script"
echo "==================================="

# Check if Docker Compose is available
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "[ERROR] Docker Compose not found."
    exit 1
fi

echo "[INFO] Stopping all services..."
$COMPOSE_CMD down -v

echo "[INFO] Removing old volumes to reset database..."
docker volume rm my-tube_postgres_data 2>/dev/null || true
docker volume rm my-tube_redis_data 2>/dev/null || true

echo "[INFO] Creating new .env file with consistent credentials..."
cat > .env << EOF
# Flask Configuration
FLASK_ENV=production
FLASK_SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Database Configuration
POSTGRES_DB=mytube
POSTGRES_USER=mytube_user
POSTGRES_PASSWORD=mytube_password_123

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Upload Configuration
MAX_CONTENT_LENGTH=2147483648
UPLOAD_FOLDER=/app/uploads

# Security
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost,http://127.0.0.1

# Video Processing
VIDEO_PROCESSING_TIMEOUT=3600
THUMBNAIL_SIZE=320x180
EOF

echo "[SUCCESS] New .env file created with consistent credentials."

echo "[INFO] Starting services with fresh database..."
$COMPOSE_CMD up -d

echo "[INFO] Waiting for database to be ready..."
sleep 30

echo "[INFO] Running database initialization..."
$COMPOSE_CMD exec backend python init_db.py

echo "[SUCCESS] Database fix complete!"
echo ""
echo "Your MyTube platform should now be accessible at:"
echo "  Web Interface: http://localhost"
echo "  Admin Panel: Use the credentials you just created"
echo ""
echo "If you still have issues, check the logs with:"
echo "  $COMPOSE_CMD logs backend"
