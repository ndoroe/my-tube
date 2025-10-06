from datetime import datetime
from app import db, bcrypt
from sqlalchemy.ext.hybrid import hybrid_property

class User(db.Model):
    """User model with role-based authentication."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum('admin', 'user', name='user_roles'), default='user', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    videos = db.relationship('Video', backref='uploader', lazy='dynamic', cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='creator', lazy='dynamic')
    
    def __init__(self, username, email, password, role='user'):
        self.username = username
        self.email = email
        self.password = password
        self.role = role
    
    @hybrid_property
    def password(self):
        """Password property getter (write-only)."""
        raise AttributeError('Password is not readable')
    
    @password.setter
    def password(self, password):
        """Hash password when setting."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == 'admin'
    
    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary."""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            data['video_count'] = self.videos.count()
            data['category_count'] = self.categories.count()
        
        return data
    
    def __repr__(self):
        return f'<User {self.username}>'
