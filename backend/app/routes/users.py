from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Video, Category

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    """Get list of users (admin only)."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    search = request.args.get('search', '').strip()
    
    query = User.query
    
    if search:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )
    
    query = query.order_by(User.created_at.desc())
    
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    users = [user.to_dict(include_sensitive=True) for user in pagination.items]
    
    return jsonify({
        'users': users,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get user details."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    target_user = User.query.get_or_404(user_id)
    
    # Users can view their own profile, admins can view any profile
    if current_user_id != user_id and not current_user.is_admin():
        return jsonify({'error': 'Permission denied'}), 403
    
    return jsonify({
        'user': target_user.to_dict(include_sensitive=True)
    }), 200

@users_bp.route('/<int:user_id>/toggle-status', methods=['POST'])
@jwt_required()
def toggle_user_status(user_id):
    """Toggle user active status (admin only)."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    target_user = User.query.get_or_404(user_id)
    
    # Prevent admin from deactivating themselves
    if current_user_id == user_id:
        return jsonify({'error': 'Cannot deactivate your own account'}), 400
    
    # Prevent deactivating the last admin
    if target_user.is_admin():
        admin_count = User.query.filter_by(role='admin', is_active=True).count()
        if admin_count <= 1:
            return jsonify({'error': 'Cannot deactivate the last admin user'}), 400
    
    target_user.is_active = not target_user.is_active
    db.session.commit()
    
    status = 'activated' if target_user.is_active else 'deactivated'
    
    return jsonify({
        'message': f'User {status} successfully',
        'user': target_user.to_dict()
    }), 200

@users_bp.route('/<int:user_id>/promote', methods=['POST'])
@jwt_required()
def promote_user(user_id):
    """Promote user to admin (admin only)."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    target_user = User.query.get_or_404(user_id)
    
    if target_user.is_admin():
        return jsonify({'error': 'User is already an admin'}), 400
    
    target_user.role = 'admin'
    db.session.commit()
    
    return jsonify({
        'message': 'User promoted to admin successfully',
        'user': target_user.to_dict()
    }), 200

@users_bp.route('/<int:user_id>/demote', methods=['POST'])
@jwt_required()
def demote_user(user_id):
    """Demote admin to regular user (admin only)."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    target_user = User.query.get_or_404(user_id)
    
    if not target_user.is_admin():
        return jsonify({'error': 'User is not an admin'}), 400
    
    # Prevent admin from demoting themselves
    if current_user_id == user_id:
        return jsonify({'error': 'Cannot demote yourself'}), 400
    
    # Prevent demoting the last admin
    admin_count = User.query.filter_by(role='admin', is_active=True).count()
    if admin_count <= 1:
        return jsonify({'error': 'Cannot demote the last admin user'}), 400
    
    target_user.role = 'user'
    db.session.commit()
    
    return jsonify({
        'message': 'User demoted to regular user successfully',
        'user': target_user.to_dict()
    }), 200

@users_bp.route('/<int:user_id>/stats', methods=['GET'])
@jwt_required()
def get_user_stats(user_id):
    """Get user statistics."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    target_user = User.query.get_or_404(user_id)
    
    # Users can view their own stats, admins can view any user's stats
    if current_user_id != user_id and not current_user.is_admin():
        return jsonify({'error': 'Permission denied'}), 403
    
    # Calculate statistics
    total_videos = target_user.videos.count()
    total_categories = target_user.categories.count()
    
    # Video statistics
    completed_videos = target_user.videos.filter_by(processing_status='completed').count()
    processing_videos = target_user.videos.filter_by(processing_status='processing').count()
    failed_videos = target_user.videos.filter_by(processing_status='failed').count()
    
    # Storage statistics
    total_storage = db.session.query(db.func.sum(Video.file_size))\
        .filter_by(uploader_id=user_id).scalar() or 0
    
    # Category statistics
    shared_categories = target_user.categories.filter_by(is_shared=True).count()
    private_categories = target_user.categories.filter_by(is_shared=False).count()
    
    return jsonify({
        'user_id': user_id,
        'username': target_user.username,
        'stats': {
            'videos': {
                'total': total_videos,
                'completed': completed_videos,
                'processing': processing_videos,
                'failed': failed_videos
            },
            'categories': {
                'total': total_categories,
                'shared': shared_categories,
                'private': private_categories
            },
            'storage': {
                'total_bytes': total_storage,
                'total_mb': round(total_storage / (1024 * 1024), 2),
                'total_gb': round(total_storage / (1024 * 1024 * 1024), 2)
            }
        }
    }), 200

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete user account (admin only)."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    target_user = User.query.get_or_404(user_id)
    
    # Prevent admin from deleting themselves
    if current_user_id == user_id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    # Prevent deleting the last admin
    if target_user.is_admin():
        admin_count = User.query.filter_by(role='admin', is_active=True).count()
        if admin_count <= 1:
            return jsonify({'error': 'Cannot delete the last admin user'}), 400
    
    # Note: Videos and categories will be cascade deleted due to foreign key constraints
    # In a production system, you might want to handle this differently
    
    username = target_user.username
    db.session.delete(target_user)
    db.session.commit()
    
    return jsonify({
        'message': f'User {username} deleted successfully'
    }), 200
