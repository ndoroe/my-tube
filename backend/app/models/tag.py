from datetime import datetime
from app import db

# Association table for many-to-many relationship between videos and tags
video_tags = db.Table('video_tags',
    db.Column('video_id', db.Integer, db.ForeignKey('videos.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class Tag(db.Model):
    """Tag model for video tagging system."""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Unique constraint: tag name per user
    __table_args__ = (
        db.UniqueConstraint('name', 'created_by', name='unique_tag_per_user'),
    )
    
    def __init__(self, name, created_by):
        self.name = name.lower().strip()  # Normalize tag names
        self.created_by = created_by
    
    def to_dict(self, include_stats=False):
        """Convert tag to dictionary."""
        data = {
            'id': self.id,
            'name': self.name,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat()
        }
        
        if include_stats:
            data['video_count'] = len(self.videos)
        
        return data
    
    @staticmethod
    def get_or_create(name, user_id):
        """Get existing tag or create new one."""
        normalized_name = name.lower().strip()
        tag = Tag.query.filter_by(name=normalized_name, created_by=user_id).first()
        
        if not tag:
            tag = Tag(name=normalized_name, created_by=user_id)
            db.session.add(tag)
        
        return tag
    
    @staticmethod
    def get_popular_tags(user_id=None, limit=20):
        """Get most popular tags, optionally filtered by user."""
        query = db.session.query(Tag, db.func.count(video_tags.c.video_id).label('count'))\
            .join(video_tags)\
            .group_by(Tag.id)\
            .order_by(db.desc('count'))
        
        if user_id:
            query = query.filter(Tag.created_by == user_id)
        
        return query.limit(limit).all()
    
    def __repr__(self):
        return f'<Tag {self.name}>'
