# MyTube API Documentation

This document describes the REST API endpoints available in MyTube.

## Base URL

```
http://localhost:5000/api
```

## Authentication

MyTube uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Response Format

All API responses follow this format:

```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message"
}
```

Error responses:

```json
{
  "success": false,
  "error": "Error message",
  "messages": { ... }  // Validation errors
}
```

## Authentication Endpoints

### POST /auth/login

Login with username and password.

**Request:**
```json
{
  "username": "admin",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "jwt-token",
  "refresh_token": "refresh-token",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "created_at": "2025-01-01T00:00:00"
  }
}
```

### POST /auth/register

Register a new user (admin only).

**Request:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123"
}
```

### POST /auth/refresh

Refresh access token using refresh token.

**Headers:**
```
Authorization: Bearer <refresh-token>
```

### GET /auth/me

Get current user information.

**Headers:**
```
Authorization: Bearer <access-token>
```

### POST /auth/change-password

Change user password.

**Request:**
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword"
}
```

## Video Endpoints

### GET /videos

Get list of videos with filtering and pagination.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 20, max: 100)
- `search` (string): Search in title and description
- `category_id` (int): Filter by category
- `uploader_id` (int): Filter by uploader

**Response:**
```json
{
  "videos": [
    {
      "id": 1,
      "title": "Sample Video",
      "description": "Video description",
      "filename": "video.mp4",
      "duration": 120.5,
      "width": 1920,
      "height": 1080,
      "processing_status": "completed",
      "uploader_username": "admin",
      "category_name": "General",
      "tags": ["tag1", "tag2"],
      "uploaded_at": "2025-01-01T00:00:00",
      "thumbnail_url": "/api/videos/1/thumbnail",
      "stream_url": "/api/videos/1/stream/original"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

### GET /videos/{id}

Get single video details.

**Response:**
```json
{
  "video": {
    "id": 1,
    "title": "Sample Video",
    "description": "Video description",
    "duration": 120.5,
    "processing_status": "completed",
    "resolutions": [
      {
        "id": 1,
        "resolution": "720p",
        "file_size": 50000000,
        "width": 1280,
        "height": 720
      }
    ]
  }
}
```

### POST /videos/upload

Upload a new video.

**Request:** Multipart form data
- `video` (file): Video file
- `title` (string): Video title
- `description` (string): Video description (optional)
- `category_id` (int): Category ID (optional)
- `tags` (array): Array of tag strings

**Response:**
```json
{
  "message": "Video uploaded successfully",
  "video": {
    "id": 1,
    "title": "New Video",
    "processing_status": "pending"
  }
}
```

### PUT /videos/{id}

Update video metadata.

**Request:**
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "category_id": 2,
  "tags": ["new", "tags"]
}
```

### DELETE /videos/{id}

Delete a video (owner or admin only).

### GET /videos/{id}/stream/{resolution}

Stream video file.

**Parameters:**
- `resolution`: "original", "720p", "1080p", etc.

### GET /videos/{id}/download/{resolution}

Download video file (authenticated users only).

### GET /videos/{id}/thumbnail

Get video thumbnail image.

## Category Endpoints

### GET /categories

Get list of accessible categories.

**Response:**
```json
{
  "categories": [
    {
      "id": 1,
      "name": "General",
      "description": "General purpose videos",
      "is_shared": true,
      "created_by": 1,
      "video_count": 10
    }
  ]
}
```

### GET /categories/{id}

Get single category details.

### POST /categories

Create a new category.

**Request:**
```json
{
  "name": "New Category",
  "description": "Category description",
  "is_shared": false
}
```

### PUT /categories/{id}

Update category (owner or admin only).

### DELETE /categories/{id}

Delete category (owner or admin only).

### POST /categories/{id}/share

Toggle category sharing status (admin only).

**Request:**
```json
{
  "is_shared": true
}
```

## User Management Endpoints

### GET /users

Get list of users (admin only).

**Query Parameters:**
- `page` (int): Page number
- `per_page` (int): Items per page
- `search` (string): Search in username and email

### GET /users/{id}

Get user details (own profile or admin).

### GET /users/{id}/stats

Get user statistics.

**Response:**
```json
{
  "stats": {
    "videos": {
      "total": 10,
      "completed": 8,
      "processing": 1,
      "failed": 1
    },
    "categories": {
      "total": 3,
      "shared": 1,
      "private": 2
    },
    "storage": {
      "total_bytes": 1000000000,
      "total_mb": 953.67,
      "total_gb": 0.93
    }
  }
}
```

### POST /users/{id}/toggle-status

Activate/deactivate user (admin only).

### POST /users/{id}/promote

Promote user to admin (admin only).

### POST /users/{id}/demote

Demote admin to user (admin only).

### DELETE /users/{id}

Delete user account (admin only).

## Admin Endpoints

### GET /admin/dashboard

Get admin dashboard statistics.

**Response:**
```json
{
  "statistics": {
    "users": {
      "total": 50,
      "active": 45,
      "admins": 2
    },
    "videos": {
      "total": 200,
      "completed": 180,
      "processing": 15,
      "failed": 5
    },
    "storage": {
      "total_bytes": 50000000000,
      "total_gb": 46.57
    }
  },
  "recent_activity": {
    "videos": [...],
    "users": [...]
  }
}
```

### GET /admin/system-info

Get system information.

**Response:**
```json
{
  "disk_usage": {
    "total_gb": 100.0,
    "used_gb": 45.2,
    "free_gb": 54.8,
    "usage_percent": 45.2
  },
  "configuration": {
    "upload_folder": "/app/uploads",
    "max_content_length": 2147483648,
    "allowed_extensions": ["mp4", "avi", "mov"],
    "video_resolutions": [...]
  }
}
```

### POST /admin/cleanup

Clean up orphaned files and failed uploads.

**Response:**
```json
{
  "stats": {
    "orphaned_files_removed": 5,
    "failed_videos_removed": 2,
    "space_freed_mb": 150.5
  }
}
```

### POST /admin/reprocess-failed

Reprocess failed videos.

### POST /admin/categories/bulk-share

Bulk update category sharing status.

**Request:**
```json
{
  "category_ids": [1, 2, 3],
  "is_shared": true
}
```

## Error Codes

- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid or missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `409` - Conflict (duplicate resource)
- `413` - Payload Too Large (file too big)
- `422` - Unprocessable Entity (validation failed)
- `500` - Internal Server Error

## Rate Limiting

- API endpoints: 10 requests per second
- Upload endpoints: 1 request per second
- Burst allowance: 20 requests for API, 5 for uploads

## File Upload Limits

- Maximum file size: 2GB (configurable)
- Supported formats: MP4, AVI, MOV, MKV, WebM, FLV, WMV, M4V, 3GP, OGV
- Processing timeout: 30 minutes per video

## Video Processing

Videos are processed asynchronously after upload:

1. **Pending**: Video uploaded, queued for processing
2. **Processing**: FFmpeg is transcoding the video
3. **Completed**: All resolutions generated successfully
4. **Failed**: Processing encountered an error

Available resolutions (generated based on source quality):
- 360p (640x360)
- 720p (1280x720)
- 1080p (1920x1080)
- 1440p (2560x1440)
- 2160p (3840x2160)

## WebSocket Events (Future)

Real-time updates for video processing status:

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:5000/ws');

// Listen for processing updates
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  if (data.type === 'video_processing') {
    console.log(`Video ${data.video_id}: ${data.status} (${data.progress}%)`);
  }
};
```

## SDK Examples

### JavaScript/Node.js

```javascript
const axios = require('axios');

class MyTubeAPI {
  constructor(baseURL, token) {
    this.client = axios.create({
      baseURL,
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    });
  }

  async login(username, password) {
    const response = await this.client.post('/auth/login', {
      username, password
    });
    return response.data;
  }

  async getVideos(params = {}) {
    const response = await this.client.get('/videos', { params });
    return response.data;
  }

  async uploadVideo(file, metadata) {
    const formData = new FormData();
    formData.append('video', file);
    Object.keys(metadata).forEach(key => {
      formData.append(key, metadata[key]);
    });

    const response = await this.client.post('/videos/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  }
}

// Usage
const api = new MyTubeAPI('http://localhost:5000/api');
const auth = await api.login('admin', 'password');
const videos = await api.getVideos({ page: 1, per_page: 10 });
```

### Python

```python
import requests
import json

class MyTubeAPI:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.session = requests.Session()
        if token:
            self.session.headers.update({'Authorization': f'Bearer {token}'})

    def login(self, username, password):
        response = self.session.post(f'{self.base_url}/auth/login', 
                                   json={'username': username, 'password': password})
        return response.json()

    def get_videos(self, **params):
        response = self.session.get(f'{self.base_url}/videos', params=params)
        return response.json()

    def upload_video(self, file_path, title, **metadata):
        with open(file_path, 'rb') as f:
            files = {'video': f}
            data = {'title': title, **metadata}
            response = self.session.post(f'{self.base_url}/videos/upload', 
                                       files=files, data=data)
        return response.json()

# Usage
api = MyTubeAPI('http://localhost:5000/api')
auth = api.login('admin', 'password')
videos = api.get_videos(page=1, per_page=10)
```
