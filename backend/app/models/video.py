import os
from datetime import datetime
from app import db
from app.models.tag import video_tags

class Video(db.Model):
    """Video model with multi-resolution support."""
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)
    duration = db.Column(db.Float)  # Duration in seconds
    thumbnail_path = db.Column(db.String(500))
    
    # Video metadata
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    fps = db.Column(db.Float)
    bitrate = db.Column(db.Integer)
    codec = db.Column(db.String(50))
    
    # Status and processing
    processing_status = db.Column(
        db.Enum('pending', 'processing', 'completed', 'failed', name='processing_status'),
        default='pending',
        nullable=False
    )
    processing_progress = db.Column(db.Integer, default=0)  # 0-100
    error_message = db.Column(db.Text)
    
    # Relationships
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    
    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    processed_at = db.Column(db.DateTime)
    
    # Many-to-many relationship with tags
    tags = db.relationship('Tag', secondary=video_tags, backref=db.backref('videos', lazy='dynamic'))
    
    # One-to-many relationship with video resolutions
    resolutions = db.relationship('VideoResolution', backref='video', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, title, filename, original_filename, file_path, file_size, uploader_id, category_id=None):
        self.title = title
        self.filename = filename
        self.original_filename = original_filename
        self.file_path = file_path
        self.file_size = file_size
        self.uploader_id = uploader_id
        self.category_id = category_id
    
    def can_access(self, user_id, user_role):
        """Check if user can access this video."""
        if user_role == 'admin':
            return True
        
        if not self.category:
            return True  # Videos without category are public
        
        return self.category.can_access(user_id)
    
    def can_modify(self, user_id, user_role):
        """Check if user can modify this video."""
        return user_role == 'admin' or self.uploader_id == user_id
    
    def can_download(self, user_id):
        """Check if user can download this video (authenticated users only)."""
        return user_id is not None
    
    def get_file_url(self, resolution=None):
        """Get URL for video file."""
        if resolution and resolution != 'original':
            video_res = self.resolutions.filter_by(resolution=resolution).first()
            if video_res:
                return f'/api/videos/{self.id}/stream/{resolution}'
        
        return f'/api/videos/{self.id}/stream/original'
    
    def get_thumbnail_url(self):
        """Get URL for video thumbnail."""
        if self.thumbnail_path:
            return f'/api/videos/{self.id}/thumbnail'
        return None
    
    def get_download_url(self, resolution='original'):
        """Get download URL for video."""
        return f'/api/videos/{self.id}/download/{resolution}'
    
    def add_tags(self, tag_names):
        """Add tags to video."""
        from app.models.tag import Tag
        
        for tag_name in tag_names:
            if tag_name.strip():
                tag = Tag.get_or_create(tag_name.strip(), self.uploader_id)
                if tag not in self.tags:
                    self.tags.append(tag)
    
    def update_processing_status(self, status, progress=None, error_message=None):
        """Update video processing status."""
        self.processing_status = status
        if progress is not None:
            self.processing_progress = progress
        if error_message:
            self.error_message = error_message
        if status == 'completed':
            self.processed_at = datetime.utcnow()
        
        db.session.commit()
    
    def to_dict(self, include_resolutions=False, include_file_paths=False):
        """Convert video to dictionary."""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'duration': self.duration,
            'width': self.width,
            'height': self.height,
            'fps': self.fps,
            'bitrate': self.bitrate,
            'codec': self.codec,
            'processing_status': self.processing_status,
            'processing_progress': self.processing_progress,
            'uploader_id': self.uploader_id,
            'uploader_username': self.uploader.username,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'uploaded_at': self.uploaded_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'tags': [tag.name for tag in self.tags],
            'thumbnail_url': self.get_thumbnail_url(),
            'stream_url': self.get_file_url(),
            'download_url': self.get_download_url()
        }
        
        if include_resolutions:
            data['resolutions'] = [res.to_dict() for res in self.resolutions]
        
        if include_file_paths:
            data['file_path'] = self.file_path
            data['thumbnail_path'] = self.thumbnail_path
        
        return data
    
    def __repr__(self):
        return f'<Video {self.title}>'

class VideoResolution(db.Model):
    """Video resolution variants for adaptive streaming."""
    __tablename__ = 'video_resolutions'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    resolution = db.Column(db.String(20), nullable=False)  # e.g., '720p', '1080p'
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)
    bitrate = db.Column(db.Integer)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __init__(self, video_id, resolution, file_path, file_size, bitrate=None, width=None, height=None):
        self.video_id = video_id
        self.resolution = resolution
        self.file_path = file_path
        self.file_size = file_size
        self.bitrate = bitrate
        self.width = width
        self.height = height
    
    def to_dict(self):
        """Convert video resolution to dictionary."""
        return {
            'id': self.id,
            'resolution': self.resolution,
            'file_size': self.file_size,
            'bitrate': self.bitrate,
            'width': self.width,
            'height': self.height,
            'stream_url': f'/api/videos/{self.video_id}/stream/{self.resolution}',
            'download_url': f'/api/videos/{self.video_id}/download/{self.resolution}'
        }
    
    def __repr__(self):
        return f'<VideoResolution {self.resolution} for Video {self.video_id}>'
