from datetime import datetime
from app import db

class Category(db.Model):
    """Category model for organizing videos."""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    is_shared = db.Column(db.Boolean, default=False, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    videos = db.relationship('Video', backref='category', lazy='dynamic')
    
    # Unique constraint: category name per user (for private categories)
    __table_args__ = (
        db.UniqueConstraint('name', 'created_by', name='unique_category_per_user'),
    )
    
    def __init__(self, name, description=None, is_shared=False, created_by=None):
        self.name = name
        self.description = description
        self.is_shared = is_shared
        self.created_by = created_by
    
    def can_access(self, user_id):
        """Check if user can access this category."""
        return self.is_shared or self.created_by == user_id
    
    def can_modify(self, user_id, user_role):
        """Check if user can modify this category."""
        return user_role == 'admin' or self.created_by == user_id
    
    def to_dict(self, include_stats=False):
        """Convert category to dictionary."""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_shared': self.is_shared,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat()
        }
        
        if include_stats:
            data['video_count'] = self.videos.count()
        
        return data
    
    @staticmethod
    def get_accessible_categories(user_id, user_role):
        """Get categories accessible to a user."""
        if user_role == 'admin':
            return Category.query.all()
        else:
            return Category.query.filter(
                db.or_(Category.is_shared == True, Category.created_by == user_id)
            ).all()
    
    def __repr__(self):
        return f'<Category {self.name}>'
