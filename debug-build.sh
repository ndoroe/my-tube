#!/bin/bash

# Debug script for MyTube Docker build issues

echo "==================================="
echo "   MyTube Build Debug Script"
echo "==================================="

# Check Docker
echo "[INFO] Checking Docker installation..."
if command -v docker &> /dev/null; then
    echo "[SUCCESS] Docker found: $(docker --version)"
else
    echo "[ERROR] Docker not found. Please install Docker first."
    exit 1
fi

# Check Docker Compose
echo "[INFO] Checking Docker Compose..."
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
    echo "[SUCCESS] Docker Compose v1 found: $(docker-compose --version)"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
    echo "[SUCCESS] Docker Compose v2 found: $(docker compose version)"
else
    echo "[ERROR] Docker Compose not found."
    exit 1
fi

# Check frontend files
echo "[INFO] Checking frontend files..."
cd frontend

if [[ ! -f "src/lib/api.js" ]]; then
    echo "[ERROR] Missing src/lib/api.js file"
    exit 1
else
    echo "[SUCCESS] Found src/lib/api.js"
fi

if [[ ! -f "package.json" ]]; then
    echo "[ERROR] Missing package.json file"
    exit 1
else
    echo "[SUCCESS] Found package.json"
fi

# Test local build
echo "[INFO] Testing local build..."
if pnpm run build; then
    echo "[SUCCESS] Local build successful"
else
    echo "[ERROR] Local build failed"
    exit 1
fi

# Clean up local build
rm -rf dist

# Go back to root
cd ..

# Try Docker build with verbose output
echo "[INFO] Attempting Docker build with verbose output..."
$COMPOSE_CMD build --no-cache --progress=plain frontend

echo "[INFO] Debug complete."
