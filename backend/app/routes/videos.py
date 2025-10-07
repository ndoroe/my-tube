import os
import uuid
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import Schema, fields, ValidationError
from werkzeug.utils import secure_filename
from app import db
from app.models import Video, VideoResolution, User, Category
from app.services.video_processor import process_video_async
from app.utils.file_utils import allowed_file, get_file_extension

videos_bp = Blueprint('videos', __name__)

class VideoUploadSchema(Schema):
    title = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    description = fields.Str(missing='')
    category_id = fields.Int(missing=None)
    tags = fields.List(fields.Str(), missing=[])

class VideoUpdateSchema(Schema):
    title = fields.Str(validate=lambda x: len(x.strip()) > 0)
    description = fields.Str()
    category_id = fields.Int(allow_none=True)
    tags = fields.List(fields.Str())

@videos_bp.route('/', methods=['GET'])
def get_videos():
    """Get list of videos with filtering and pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('search', '').strip()
    uploader_id = request.args.get('uploader_id', type=int)
    
    # Get current user if authenticated
    current_user_id = None
    user_role = None
    try:
        current_user_id = int(get_jwt_identity())
        if current_user_id:
            user = User.query.get(current_user_id)
            user_role = user.role if user else None
    except:
        pass
    
    # Build query
    query = Video.query.filter_by(processing_status='completed')
    
    # Filter by category access
    if category_id:
        category = Category.query.get(category_id)
        if not category or not category.can_access(current_user_id):
            return jsonify({'error': 'Category not accessible'}), 403
        query = query.filter_by(category_id=category_id)
    elif current_user_id:
        # Show videos from accessible categories
        accessible_categories = Category.get_accessible_categories(current_user_id, user_role)
        category_ids = [cat.id for cat in accessible_categories]
        query = query.filter(
            db.or_(Video.category_id.in_(category_ids), Video.category_id.is_(None))
        )
    else:
        # Public access - only shared categories and uncategorized videos
        shared_categories = Category.query.filter_by(is_shared=True).all()
        category_ids = [cat.id for cat in shared_categories]
        query = query.filter(
            db.or_(Video.category_id.in_(category_ids), Video.category_id.is_(None))
        )
    
    # Apply filters
    if search:
        query = query.filter(
            db.or_(
                Video.title.ilike(f'%{search}%'),
                Video.description.ilike(f'%{search}%')
            )
        )
    
    if uploader_id:
        query = query.filter_by(uploader_id=uploader_id)
    
    # Order by upload date (newest first)
    query = query.order_by(Video.uploaded_at.desc())
    
    # Paginate
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    videos = [video.to_dict() for video in pagination.items]
    
    return jsonify({
        'videos': videos,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200

@videos_bp.route('/<int:video_id>', methods=['GET'])
def get_video(video_id):
    """Get single video details."""
    video = Video.query.get_or_404(video_id)
    
    # Check access permissions
    current_user_id = None
    user_role = None
    try:
        current_user_id = int(get_jwt_identity())
        if current_user_id:
            user = User.query.get(current_user_id)
            user_role = user.role if user else None
    except:
        pass
    
    if not video.can_access(current_user_id, user_role):
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'video': video.to_dict(include_resolutions=True)
    }), 200

@videos_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_video():
    """Upload a new video."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({'error': 'User not found or inactive'}), 404
    
    # Check if file is present
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    if not allowed_file(file.filename, current_app.config['ALLOWED_VIDEO_EXTENSIONS']):
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Validate form data
    try:
        schema = VideoUploadSchema()
        form_data = {
            'title': request.form.get('title', ''),
            'description': request.form.get('description', ''),
            'category_id': request.form.get('category_id'),
            'tags': request.form.getlist('tags')
        }
        
        if form_data['category_id']:
            form_data['category_id'] = int(form_data['category_id'])
        
        data = schema.load(form_data)
    except (ValidationError, ValueError) as err:
        return jsonify({'error': 'Validation error', 'messages': str(err)}), 400
    
    # Check category access
    if data['category_id']:
        category = Category.query.get(data['category_id'])
        if not category or not category.can_access(current_user_id):
            return jsonify({'error': 'Category not accessible'}), 403
    
    # Generate unique filename
    original_filename = secure_filename(file.filename)
    file_extension = get_file_extension(original_filename)
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    
    # Save file
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'videos', unique_filename)
    file.save(upload_path)
    
    # Get file size
    file_size = os.path.getsize(upload_path)
    
    # Create video record
    video = Video(
        title=data['title'],
        filename=unique_filename,
        original_filename=original_filename,
        file_path=upload_path,
        file_size=file_size,
        uploader_id=current_user_id,
        category_id=data['category_id']
    )
    
    video.description = data['description']
    
    db.session.add(video)
    db.session.commit()
    
    # Add tags
    if data['tags']:
        video.add_tags(data['tags'])
        db.session.commit()
    
    # Start background processing
    process_video_async.delay(video.id)
    
    return jsonify({
        'message': 'Video uploaded successfully',
        'video': video.to_dict()
    }), 201

@videos_bp.route('/<int:video_id>', methods=['PUT'])
@jwt_required()
def update_video(video_id):
    """Update video metadata."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    video = Video.query.get_or_404(video_id)
    
    if not video.can_modify(current_user_id, user.role):
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        schema = VideoUpdateSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    # Update fields
    if 'title' in data:
        video.title = data['title']
    if 'description' in data:
        video.description = data['description']
    if 'category_id' in data:
        if data['category_id']:
            category = Category.query.get(data['category_id'])
            if not category or not category.can_access(current_user_id):
                return jsonify({'error': 'Category not accessible'}), 403
        video.category_id = data['category_id']
    
    # Update tags
    if 'tags' in data:
        # Clear existing tags
        video.tags.clear()
        # Add new tags
        if data['tags']:
            video.add_tags(data['tags'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Video updated successfully',
        'video': video.to_dict()
    }), 200

@videos_bp.route('/<int:video_id>', methods=['DELETE'])
@jwt_required()
def delete_video(video_id):
    """Delete a video."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    video = Video.query.get_or_404(video_id)
    
    if not video.can_modify(current_user_id, user.role):
        return jsonify({'error': 'Permission denied'}), 403
    
    # Delete files
    try:
        if os.path.exists(video.file_path):
            os.remove(video.file_path)
        if video.thumbnail_path and os.path.exists(video.thumbnail_path):
            os.remove(video.thumbnail_path)
        
        # Delete resolution files
        for resolution in video.resolutions:
            if os.path.exists(resolution.file_path):
                os.remove(resolution.file_path)
    except OSError:
        pass  # Continue even if file deletion fails
    
    # Delete database record
    db.session.delete(video)
    db.session.commit()
    
    return jsonify({'message': 'Video deleted successfully'}), 200

@videos_bp.route('/<int:video_id>/stream/<resolution>', methods=['GET'])
def stream_video(video_id, resolution):
    """Stream video file."""
    video = Video.query.get_or_404(video_id)
    
    # Check access permissions
    current_user_id = None
    user_role = None
    try:
        current_user_id = int(get_jwt_identity())
        if current_user_id:
            user = User.query.get(current_user_id)
            user_role = user.role if user else None
    except:
        pass
    
    if not video.can_access(current_user_id, user_role):
        return jsonify({'error': 'Access denied'}), 403
    
    # Get file path
    if resolution == 'original':
        file_path = video.file_path
    else:
        video_res = video.resolutions.filter_by(resolution=resolution).first()
        if not video_res:
            return jsonify({'error': 'Resolution not available'}), 404
        file_path = video_res.file_path
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(file_path, as_attachment=False)

@videos_bp.route('/<int:video_id>/download/<resolution>', methods=['GET'])
@jwt_required()
def download_video(video_id, resolution):
    """Download video file."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    video = Video.query.get_or_404(video_id)
    
    if not video.can_access(current_user_id, user.role):
        return jsonify({'error': 'Access denied'}), 403
    
    if not video.can_download(current_user_id):
        return jsonify({'error': 'Download requires authentication'}), 403
    
    # Get file path and name
    if resolution == 'original':
        file_path = video.file_path
        filename = video.original_filename
    else:
        video_res = video.resolutions.filter_by(resolution=resolution).first()
        if not video_res:
            return jsonify({'error': 'Resolution not available'}), 404
        file_path = video_res.file_path
        name, ext = os.path.splitext(video.original_filename)
        filename = f"{name}_{resolution}{ext}"
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(file_path, as_attachment=True, download_name=filename)

@videos_bp.route('/<int:video_id>/thumbnail', methods=['GET'])
def get_thumbnail(video_id):
    """Get video thumbnail."""
    video = Video.query.get_or_404(video_id)
    
    # Check access permissions
    current_user_id = None
    user_role = None
    try:
        current_user_id = int(get_jwt_identity())
        if current_user_id:
            user = User.query.get(current_user_id)
            user_role = user.role if user else None
    except:
        pass
    
    if not video.can_access(current_user_id, user_role):
        return jsonify({'error': 'Access denied'}), 403
    
    if not video.thumbnail_path or not os.path.exists(video.thumbnail_path):
        return jsonify({'error': 'Thumbnail not found'}), 404
    
    return send_file(video.thumbnail_path, as_attachment=False)
