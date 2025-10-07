# MyTube Testing Guide

This document outlines testing procedures for MyTube to ensure all components work correctly.

## Recent Test Updates

- **JWT Authentication**: Added tests for string identity JWT tokens
- **Upload Functionality**: Verified video upload fixes (HTTP 422 resolution)
- **CORS Testing**: Multi-domain CORS configuration validation
- **Health Checks**: Container health monitoring tests

## Table of Contents

1. [Testing Overview](#testing-overview)
2. [Prerequisites](#prerequisites)
3. [Backend Testing](#backend-testing)
4. [Frontend Testing](#frontend-testing)
5. [Integration Testing](#integration-testing)
6. [Performance Testing](#performance-testing)
7. [Security Testing](#security-testing)
8. [Deployment Testing](#deployment-testing)

## Testing Overview

MyTube testing covers:
- **Unit Tests**: Individual component functionality
- **Integration Tests**: Component interaction
- **End-to-End Tests**: Complete user workflows
- **Performance Tests**: System performance under load
- **Security Tests**: Authentication and authorization

## Prerequisites

### Test Environment Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/my-tube.git
cd my-tube

# Install test dependencies
cd backend
pip install -r requirements-test.txt

cd ../frontend
pnpm install
```

### Test Data

Create test video files:

```bash
# Create test videos directory
mkdir -p test-data/videos

# Generate test video files (requires ffmpeg)
ffmpeg -f lavfi -i testsrc=duration=10:size=1280x720:rate=30 \
  -c:v libx264 test-data/videos/test-720p.mp4

ffmpeg -f lavfi -i testsrc=duration=5:size=640x360:rate=30 \
  -c:v libx264 test-data/videos/test-360p.mp4
```

## Backend Testing

### Unit Tests

```bash
cd backend

# Run all unit tests
python -m pytest tests/ -v

# Run specific test modules
python -m pytest tests/test_models.py -v
python -m pytest tests/test_auth.py -v
python -m pytest tests/test_videos.py -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

### API Testing

#### Authentication Tests

```bash
# Test user registration (admin only)
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin-token>" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }'

# Test login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your-admin-password"
  }'

# Test token refresh
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer <refresh-token>"

# Test user info
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer <access-token>"
```

#### Video API Tests

```bash
# Get videos list
curl -X GET "http://localhost:5000/api/videos?page=1&per_page=10"

# Upload video
curl -X POST http://localhost:5000/api/videos/upload \
  -H "Authorization: Bearer <access-token>" \
  -F "video=@test-data/videos/test-720p.mp4" \
  -F "title=Test Video" \
  -F "description=Test video description"

# Get video details
curl -X GET http://localhost:5000/api/videos/1 \
  -H "Authorization: Bearer <access-token>"

# Update video
curl -X PUT http://localhost:5000/api/videos/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access-token>" \
  -d '{
    "title": "Updated Title",
    "description": "Updated description"
  }'

# Delete video
curl -X DELETE http://localhost:5000/api/videos/1 \
  -H "Authorization: Bearer <access-token>"
```

#### Category API Tests

```bash
# Get categories
curl -X GET http://localhost:5000/api/categories

# Create category
curl -X POST http://localhost:5000/api/categories \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access-token>" \
  -d '{
    "name": "Test Category",
    "description": "Test category description",
    "is_shared": false
  }'

# Update category
curl -X PUT http://localhost:5000/api/categories/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access-token>" \
  -d '{
    "name": "Updated Category",
    "is_shared": true
  }'
```

### Database Tests

```bash
# Test database connection
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    try:
        db.engine.execute('SELECT 1')
        print('Database connection: OK')
    except Exception as e:
        print(f'Database connection failed: {e}')
"

# Test model creation
python -c "
from app import create_app, db
from app.models import User, Video, Category
app = create_app()
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"
```

### JWT Authentication Tests

Test the fixed JWT authentication system:

```bash
# Test login and token generation
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'

# Expected: JWT token with string identity
# Verify token format (should have "sub": "1" not "sub": 1)

# Test protected endpoint
TOKEN="your-jwt-token-here"
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/auth/me

# Expected: User information without JWT errors

# Test video upload with JWT
curl -X POST http://localhost:5000/api/videos/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "video=@test-video.mp4" \
  -F "title=Test Video" \
  -F "description=Test upload" \
  -F "category_id=1"

# Expected: Success response, no HTTP 422 error
```

### CORS Configuration Tests

Test multi-domain CORS setup:

```bash
# Test CORS from different origins
curl -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: authorization,content-type" \
  -X OPTIONS http://localhost:5000/api/videos/upload

# Expected: CORS headers in response

# Test with configured domain
curl -H "Origin: https://yourdomain.com" \
  -H "Access-Control-Request-Method: GET" \
  -X OPTIONS http://localhost:5000/api/videos

# Expected: Access-Control-Allow-Origin header with yourdomain.com
```

### Container Health Tests

Test container health monitoring:

```bash
# Check container health status
docker-compose ps

# Expected: All containers should show "healthy" status

# Test health check endpoint directly
curl -f http://localhost:5000/api/categories/

# Expected: Categories list without authentication error

# Monitor health check logs
docker-compose logs backend | grep health

# Expected: No authentication failures in health checks
```

### Video Processing Tests

```bash
# Test FFmpeg availability
python -c "
import subprocess
try:
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
    print('FFmpeg available:', result.returncode == 0)
except FileNotFoundError:
    print('FFmpeg not found')
"

# Test video processing
python -c "
from app.services.video_processor import get_video_info, validate_video_file
info = get_video_info('test-data/videos/test-720p.mp4')
print('Video info:', info)
valid = validate_video_file('test-data/videos/test-720p.mp4')
print('Video valid:', valid)
"
```

## Frontend Testing

### Component Tests

```bash
cd frontend

# Run component tests
pnpm test

# Run tests in watch mode
pnpm test:watch

# Run tests with coverage
pnpm test:coverage
```

### E2E Tests with Playwright

```bash
# Install Playwright
pnpm exec playwright install

# Run E2E tests
pnpm test:e2e

# Run tests in headed mode
pnpm test:e2e --headed

# Run specific test file
pnpm exec playwright test tests/auth.spec.js
```

### Manual Frontend Testing

#### Authentication Flow

1. **Login Page**:
   - Navigate to `/login`
   - Enter valid credentials
   - Verify successful login and redirect
   - Test invalid credentials
   - Test form validation

2. **Registration** (Admin only):
   - Navigate to admin panel
   - Create new user
   - Verify user creation
   - Test validation errors

#### Video Management

1. **Video Upload**:
   - Navigate to `/upload`
   - Select video file
   - Fill in metadata
   - Submit form
   - Verify upload progress
   - Check processing status

2. **Video Browsing**:
   - Navigate to home page
   - Test video grid display
   - Test search functionality
   - Test category filtering
   - Test pagination

3. **Video Playback**:
   - Click on video
   - Verify player loads
   - Test video controls
   - Test quality selection
   - Test fullscreen mode

#### Category Management

1. **Category Creation**:
   - Navigate to `/categories`
   - Create new category
   - Test form validation
   - Verify category appears

2. **Category Sharing** (Admin):
   - Toggle category sharing
   - Verify sharing status
   - Test access permissions

## Integration Testing

### Full Stack Tests

```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Wait for services to be ready
sleep 30

# Run integration tests
python -m pytest tests/integration/ -v

# Cleanup
docker-compose -f docker-compose.test.yml down -v
```

### API Integration Tests

```python
# tests/integration/test_video_workflow.py
import pytest
import requests
import time

class TestVideoWorkflow:
    def test_complete_video_workflow(self):
        base_url = "http://localhost:5000/api"
        
        # 1. Login
        login_response = requests.post(f"{base_url}/auth/login", json={
            "username": "admin",
            "password": "admin_password"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Create category
        category_response = requests.post(f"{base_url}/categories", 
            json={"name": "Test Category"}, headers=headers)
        assert category_response.status_code == 201
        category_id = category_response.json()["data"]["category"]["id"]
        
        # 3. Upload video
        with open("test-data/videos/test-720p.mp4", "rb") as f:
            upload_response = requests.post(f"{base_url}/videos/upload",
                files={"video": f},
                data={"title": "Test Video", "category_id": category_id},
                headers=headers)
        assert upload_response.status_code == 201
        video_id = upload_response.json()["data"]["video"]["id"]
        
        # 4. Wait for processing
        max_wait = 300  # 5 minutes
        start_time = time.time()
        while time.time() - start_time < max_wait:
            video_response = requests.get(f"{base_url}/videos/{video_id}")
            video_data = video_response.json()["data"]["video"]
            if video_data["processing_status"] == "completed":
                break
            time.sleep(10)
        
        assert video_data["processing_status"] == "completed"
        
        # 5. Test video streaming
        stream_response = requests.get(f"{base_url}/videos/{video_id}/stream/original")
        assert stream_response.status_code == 200
        
        # 6. Test video download (authenticated)
        download_response = requests.get(f"{base_url}/videos/{video_id}/download/original", 
                                       headers=headers)
        assert download_response.status_code == 200
        
        # 7. Cleanup
        requests.delete(f"{base_url}/videos/{video_id}", headers=headers)
        requests.delete(f"{base_url}/categories/{category_id}", headers=headers)
```

## Performance Testing

### Load Testing with Locust

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between

class MyTubeUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpass"
        })
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def browse_videos(self):
        self.client.get("/api/videos")
    
    @task(2)
    def view_video(self):
        self.client.get("/api/videos/1")
    
    @task(1)
    def stream_video(self):
        self.client.get("/api/videos/1/stream/720p")

# Run load test
# locust -f tests/performance/locustfile.py --host=http://localhost:5000
```

### Database Performance

```sql
-- Test queries for performance
EXPLAIN ANALYZE SELECT * FROM videos WHERE processing_status = 'completed';
EXPLAIN ANALYZE SELECT * FROM videos WHERE uploader_id = 1;
EXPLAIN ANALYZE SELECT v.*, c.name as category_name 
FROM videos v LEFT JOIN categories c ON v.category_id = c.id;

-- Check for missing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation 
FROM pg_stats WHERE schemaname = 'public';
```

## Security Testing

### Authentication Security

```bash
# Test JWT token validation
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer invalid-token"

# Test expired token
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer <expired-token>"

# Test unauthorized access
curl -X POST http://localhost:5000/api/videos/upload \
  -F "video=@test-video.mp4"
```

### Input Validation

```bash
# Test SQL injection
curl -X GET "http://localhost:5000/api/videos?search='; DROP TABLE videos; --"

# Test XSS
curl -X POST http://localhost:5000/api/categories \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"name": "<script>alert(\"xss\")</script>"}'

# Test file upload validation
curl -X POST http://localhost:5000/api/videos/upload \
  -H "Authorization: Bearer <token>" \
  -F "video=@malicious.exe" \
  -F "title=Test"
```

### Permission Testing

```bash
# Test admin-only endpoints as regular user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Authorization: Bearer <user-token>" \
  -d '{"username": "test", "password": "test"}'

# Test accessing other users' private content
curl -X GET http://localhost:5000/api/videos/private-video-id \
  -H "Authorization: Bearer <other-user-token>"
```

## Deployment Testing

### Docker Testing

```bash
# Test Docker build
docker-compose build

# Test services startup
docker-compose up -d

# Check service health
docker-compose ps
docker-compose logs

# Test service connectivity
curl http://localhost/health
curl http://localhost/api/auth/me

# Test volume persistence
docker-compose down
docker-compose up -d
# Verify data persists
```

### Installation Script Testing

```bash
# Test installation script
./install.sh --check

# Test in clean environment
docker run -it --rm ubuntu:22.04 bash
# Inside container:
apt update && apt install -y git curl
git clone https://github.com/yourusername/my-tube.git
cd my-tube
./install.sh
```

## Test Automation

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test MyTube

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      run: |
        cd backend
        python -m pytest tests/ -v --cov=app
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install frontend dependencies
      run: |
        cd frontend
        npm install -g pnpm
        pnpm install
    
    - name: Run frontend tests
      run: |
        cd frontend
        pnpm test
```

## Test Checklist

### Pre-deployment Checklist

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] API endpoints respond correctly
- [ ] Authentication works
- [ ] Video upload works
- [ ] Video processing works
- [ ] Video streaming works
- [ ] Category management works
- [ ] User management works (admin)
- [ ] Frontend loads correctly
- [ ] All pages accessible
- [ ] Responsive design works
- [ ] Error handling works
- [ ] Security validations work
- [ ] Performance is acceptable
- [ ] Docker containers start
- [ ] Installation script works

### Post-deployment Checklist

- [ ] Application accessible via web
- [ ] SSL certificate valid (production)
- [ ] Database backups working
- [ ] Log rotation configured
- [ ] Monitoring alerts working
- [ ] Performance metrics normal
- [ ] Security scans clean
- [ ] Documentation up to date

## Troubleshooting Tests

### Common Test Failures

1. **Database Connection Failed**:
   ```bash
   # Check PostgreSQL service
   docker-compose logs postgres
   
   # Verify connection string
   echo $DATABASE_URL
   ```

2. **Video Processing Failed**:
   ```bash
   # Check FFmpeg installation
   docker-compose exec backend ffmpeg -version
   
   # Check Celery worker
   docker-compose logs celery_worker
   ```

3. **Frontend Tests Failed**:
   ```bash
   # Clear node modules
   rm -rf node_modules package-lock.json
   pnpm install
   
   # Check for port conflicts
   lsof -i :3000
   ```

4. **API Tests Failed**:
   ```bash
   # Check backend logs
   docker-compose logs backend
   
   # Verify API is running
   curl http://localhost:5000/api/auth/me
   ```

### Test Data Cleanup

```bash
# Clean test database
docker-compose exec postgres psql -U mytube_user -d mytube -c "
  DELETE FROM video_resolutions;
  DELETE FROM videos;
  DELETE FROM categories WHERE name LIKE 'Test%';
  DELETE FROM users WHERE username LIKE 'test%';
"

# Clean test files
rm -rf uploads/test-*
rm -rf test-data/
```

This comprehensive testing guide ensures MyTube works correctly across all components and scenarios.
