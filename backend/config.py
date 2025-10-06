import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"postgresql://{os.environ.get('POSTGRES_USER', 'mytube_user')}:" \
        f"{os.environ.get('POSTGRES_PASSWORD', 'password')}@" \
        f"{os.environ.get('POSTGRES_HOST', 'localhost')}:" \
        f"{os.environ.get('POSTGRES_PORT', '5432')}/" \
        f"{os.environ.get('POSTGRES_DB', 'mytube')}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or '/app/uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 2147483648))  # 2GB
    ALLOWED_VIDEO_EXTENSIONS = {
        'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'm4v', '3gp', 'ogv'
    }
    
    # Video Processing
    VIDEO_RESOLUTIONS = [
        {'name': '360p', 'height': 360, 'bitrate': '800k'},
        {'name': '720p', 'height': 720, 'bitrate': '2500k'},
        {'name': '1080p', 'height': 1080, 'bitrate': '5000k'},
        {'name': '1440p', 'height': 1440, 'bitrate': '10000k'},
        {'name': '2160p', 'height': 2160, 'bitrate': '20000k'}
    ]
    
    # Celery
    CELERY_BROKER_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
