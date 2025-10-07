# MyTube Changelog

All notable changes to the MyTube project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-10-06

### 🔧 Fixed

#### JWT Authentication System
- **Fixed JWT Token Identity Format**: Resolved "Subject must be a string" errors by converting JWT identity from integer to string format
- **Updated Token Creation**: Modified `create_access_token()` and `create_refresh_token()` to use `str(user.id)` instead of `user.id`
- **Fixed Token Validation**: Updated `get_jwt_identity()` usage across all endpoints to handle string identities properly
- **Resolved HTTP 422 Upload Errors**: Video uploads now work correctly after JWT authentication fixes

#### Container Health Monitoring
- **Fixed Backend Health Check**: Changed health check endpoint from `/api/auth/me` (authenticated) to `/api/categories/` (unauthenticated)
- **Resolved Container Status Issues**: Backend containers now properly report healthy status
- **Updated Docker Compose**: Modified health check configuration in `docker-compose.yml`

#### CORS and Multi-Domain Support
- **Enhanced CORS Configuration**: Improved CORS handling in nginx reverse proxy
- **Added Allowed Hosts Configuration**: Support for multiple domains via `ALLOWED_HOSTS` environment variable
- **Fixed CORS Origins**: Proper CORS origin validation for cross-domain requests
- **Nginx Configuration Updates**: Fixed nested if statements and improved CORS header handling

### ✨ Added

#### Multi-Domain Deployment
- **Configurable Allowed Hosts**: Support for multiple domains and IP addresses
- **Environment Variable Configuration**: `ALLOWED_HOSTS` and `CORS_ORIGINS` environment variables
- **Flexible CORS Setup**: Configure multiple origins for cross-domain access

#### Improved Documentation
- **Updated README.md**: Added troubleshooting section and configuration examples
- **Enhanced API Documentation**: Added troubleshooting section for common API errors
- **Updated Deployment Guide**: Added multi-domain configuration and recent fixes
- **Enhanced Testing Guide**: Added tests for JWT authentication and CORS configuration
- **Created Changelog**: Comprehensive changelog for tracking project updates

### 🔄 Changed

#### Backend Authentication
- **JWT Identity Handling**: All `get_jwt_identity()` calls now convert string to integer for database queries
- **Auth Route Updates**: Updated login, refresh, and user registration endpoints
- **Video Route Updates**: Fixed video upload endpoint JWT handling
- **User Route Updates**: Updated user management endpoints for string identity compatibility

#### Configuration Management
- **Environment Variables**: Added new configuration options for multi-domain support
- **Docker Health Checks**: Improved health check reliability and accuracy
- **Nginx Configuration**: Enhanced reverse proxy configuration for better CORS handling

## [1.0.0] - 2025-10-05

### Initial Release

#### Core Features
- **Video Management**: Upload, transcode, and stream videos in multiple formats
- **User Authentication**: JWT-based authentication with role-based access control
- **Content Organization**: Categories and tags for video organization
- **Admin Interface**: Complete admin panel for user and content management
- **Responsive Design**: Mobile-first responsive web interface

#### Technical Stack
- **Backend**: Flask (Python) with SQLAlchemy ORM
- **Frontend**: React with Tailwind CSS and shadcn/ui components
- **Database**: PostgreSQL for production-grade performance
- **Cache/Queue**: Redis for caching and background task processing
- **Video Processing**: FFmpeg for transcoding and thumbnail generation
- **Containerization**: Docker and Docker Compose for easy deployment

#### Security Features
- **Admin-Only Registration**: Controlled user creation for security
- **Role-Based Access Control**: Separate permissions for users and admins
- **File Validation**: Comprehensive upload security checks
- **JWT Authentication**: Secure token-based authentication system

---

## Contributing

When adding entries to this changelog:

1. **Use semantic versioning** (MAJOR.MINOR.PATCH)
2. **Categorize changes** using:
   - `Added` for new features
   - `Changed` for changes in existing functionality
   - `Deprecated` for soon-to-be removed features
   - `Removed` for now removed features
   - `Fixed` for any bug fixes
   - `Security` for vulnerability fixes

3. **Include relevant details**:
   - What was the issue?
   - How was it fixed?
   - What files were modified?
   - Any breaking changes?

4. **Reference related issues/PRs** when applicable

## Links

- [Repository](https://github.com/ndoroe/my-tube)
- [Documentation](./docs/)
- [Installation Guide](./QUICK_START.md)
- [API Documentation](./docs/API.md)