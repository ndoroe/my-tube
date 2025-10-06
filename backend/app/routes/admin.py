import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from app import db
from app.models import User, Video, Category, Tag

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get admin dashboard statistics."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    # User statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    admin_users = User.query.filter_by(role='admin').count()
    
    # Video statistics
    total_videos = Video.query.count()
    completed_videos = Video.query.filter_by(processing_status='completed').count()
    processing_videos = Video.query.filter_by(processing_status='processing').count()
    failed_videos = Video.query.filter_by(processing_status='failed').count()
    
    # Category statistics
    total_categories = Category.query.count()
    shared_categories = Category.query.filter_by(is_shared=True).count()
    
    # Tag statistics
    total_tags = Tag.query.count()
    
    # Storage statistics
    total_storage = db.session.query(func.sum(Video.file_size)).scalar() or 0
    
    # Recent activity
    recent_videos = Video.query.order_by(Video.uploaded_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # Top uploaders
    top_uploaders = db.session.query(
        User.username,
        func.count(Video.id).label('video_count'),
        func.sum(Video.file_size).label('total_size')
    ).join(Video).group_by(User.id).order_by(func.count(Video.id).desc()).limit(5).all()
    
    return jsonify({
        'statistics': {
            'users': {
                'total': total_users,
                'active': active_users,
                'admins': admin_users,
                'inactive': total_users - active_users
            },
            'videos': {
                'total': total_videos,
                'completed': completed_videos,
                'processing': processing_videos,
                'failed': failed_videos
            },
            'categories': {
                'total': total_categories,
                'shared': shared_categories,
                'private': total_categories - shared_categories
            },
            'tags': {
                'total': total_tags
            },
            'storage': {
                'total_bytes': total_storage,
                'total_mb': round(total_storage / (1024 * 1024), 2),
                'total_gb': round(total_storage / (1024 * 1024 * 1024), 2)
            }
        },
        'recent_activity': {
            'videos': [video.to_dict() for video in recent_videos],
            'users': [user.to_dict() for user in recent_users]
        },
        'top_uploaders': [
            {
                'username': uploader.username,
                'video_count': uploader.video_count,
                'total_size_mb': round(uploader.total_size / (1024 * 1024), 2)
            }
            for uploader in top_uploaders
        ]
    }), 200

@admin_bp.route('/system-info', methods=['GET'])
@jwt_required()
def get_system_info():
    """Get system information."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get disk usage for upload directory
    upload_folder = current_app.config['UPLOAD_FOLDER']
    disk_usage = {'total': 0, 'used': 0, 'free': 0}
    
    try:
        if os.path.exists(upload_folder):
            statvfs = os.statvfs(upload_folder)
            disk_usage = {
                'total': statvfs.f_frsize * statvfs.f_blocks,
                'free': statvfs.f_frsize * statvfs.f_available,
                'used': statvfs.f_frsize * (statvfs.f_blocks - statvfs.f_available)
            }
    except:
        pass
    
    # Get configuration info
    config_info = {
        'upload_folder': upload_folder,
        'max_content_length': current_app.config.get('MAX_CONTENT_LENGTH', 0),
        'allowed_extensions': list(current_app.config.get('ALLOWED_VIDEO_EXTENSIONS', [])),
        'video_resolutions': current_app.config.get('VIDEO_RESOLUTIONS', [])
    }
    
    return jsonify({
        'disk_usage': {
            'total_bytes': disk_usage['total'],
            'used_bytes': disk_usage['used'],
            'free_bytes': disk_usage['free'],
            'total_gb': round(disk_usage['total'] / (1024**3), 2),
            'used_gb': round(disk_usage['used'] / (1024**3), 2),
            'free_gb': round(disk_usage['free'] / (1024**3), 2),
            'usage_percent': round((disk_usage['used'] / disk_usage['total']) * 100, 2) if disk_usage['total'] > 0 else 0
        },
        'configuration': config_info
    }), 200

@admin_bp.route('/cleanup', methods=['POST'])
@jwt_required()
def cleanup_system():
    """Clean up orphaned files and failed uploads."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    cleanup_stats = {
        'orphaned_files_removed': 0,
        'failed_videos_removed': 0,
        'space_freed_bytes': 0
    }
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    # Clean up failed video records
    failed_videos = Video.query.filter_by(processing_status='failed').all()
    for video in failed_videos:
        # Remove files if they exist
        for file_path in [video.file_path, video.thumbnail_path]:
            if file_path and os.path.exists(file_path):
                try:
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    cleanup_stats['space_freed_bytes'] += file_size
                except:
                    pass
        
        # Remove resolution files
        for resolution in video.resolutions:
            if os.path.exists(resolution.file_path):
                try:
                    file_size = os.path.getsize(resolution.file_path)
                    os.remove(resolution.file_path)
                    cleanup_stats['space_freed_bytes'] += file_size
                except:
                    pass
        
        db.session.delete(video)
        cleanup_stats['failed_videos_removed'] += 1
    
    # Find orphaned files
    if os.path.exists(upload_folder):
        # Get all file paths from database
        db_files = set()
        for video in Video.query.all():
            if video.file_path:
                db_files.add(video.file_path)
            if video.thumbnail_path:
                db_files.add(video.thumbnail_path)
            for resolution in video.resolutions:
                db_files.add(resolution.file_path)
        
        # Check for orphaned files
        for root, dirs, files in os.walk(upload_folder):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path not in db_files:
                    try:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        cleanup_stats['orphaned_files_removed'] += 1
                        cleanup_stats['space_freed_bytes'] += file_size
                    except:
                        pass
    
    db.session.commit()
    
    return jsonify({
        'message': 'System cleanup completed',
        'stats': {
            **cleanup_stats,
            'space_freed_mb': round(cleanup_stats['space_freed_bytes'] / (1024 * 1024), 2),
            'space_freed_gb': round(cleanup_stats['space_freed_bytes'] / (1024 * 1024 * 1024), 2)
        }
    }), 200

@admin_bp.route('/reprocess-failed', methods=['POST'])
@jwt_required()
def reprocess_failed_videos():
    """Reprocess failed videos."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    from app.services.video_processor import process_video_async
    
    failed_videos = Video.query.filter_by(processing_status='failed').all()
    reprocessed_count = 0
    
    for video in failed_videos:
        if os.path.exists(video.file_path):
            video.processing_status = 'pending'
            video.processing_progress = 0
            video.error_message = None
            db.session.commit()
            
            # Start background processing
            process_video_async.delay(video.id)
            reprocessed_count += 1
    
    return jsonify({
        'message': f'Reprocessing {reprocessed_count} failed videos',
        'count': reprocessed_count
    }), 200

@admin_bp.route('/categories/bulk-share', methods=['POST'])
@jwt_required()
def bulk_share_categories():
    """Bulk update category sharing status."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    category_ids = data.get('category_ids', [])
    is_shared = data.get('is_shared', True)
    
    if not category_ids:
        return jsonify({'error': 'No categories specified'}), 400
    
    updated_count = Category.query.filter(Category.id.in_(category_ids))\
        .update({'is_shared': is_shared}, synchronize_session=False)
    
    db.session.commit()
    
    action = 'shared' if is_shared else 'unshared'
    
    return jsonify({
        'message': f'{updated_count} categories {action} successfully',
        'count': updated_count
    }), 200
