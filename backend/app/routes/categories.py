from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from app import db
from app.models import Category, User

categories_bp = Blueprint('categories', __name__)

class CategorySchema(Schema):
    name = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    description = fields.Str(missing='')
    is_shared = fields.Bool(missing=False)

@categories_bp.route('/', methods=['GET'])
def get_categories():
    """Get list of categories accessible to the user."""
    current_user_id = None
    user_role = None
    
    try:
        current_user_id = int(get_jwt_identity())
        if current_user_id:
            user = User.query.get(current_user_id)
            user_role = user.role if user else None
    except:
        pass
    
    if current_user_id:
        categories = Category.get_accessible_categories(current_user_id, user_role)
    else:
        # Public access - only shared categories
        categories = Category.query.filter_by(is_shared=True).all()
    
    return jsonify({
        'categories': [cat.to_dict(include_stats=True) for cat in categories]
    }), 200

@categories_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Get single category details."""
    category = Category.query.get_or_404(category_id)
    
    # Check access permissions
    current_user_id = None
    try:
        current_user_id = int(get_jwt_identity())
    except:
        pass
    
    if not category.can_access(current_user_id):
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'category': category.to_dict(include_stats=True)
    }), 200

@categories_bp.route('/', methods=['POST'])
@jwt_required()
def create_category():
    """Create a new category."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({'error': 'User not found or inactive'}), 404
    
    try:
        schema = CategorySchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    # Check if category name already exists for this user
    existing = Category.query.filter_by(
        name=data['name'], 
        created_by=current_user_id
    ).first()
    
    if existing:
        return jsonify({'error': 'Category name already exists'}), 409
    
    # Only admins can create shared categories
    if data['is_shared'] and not user.is_admin():
        return jsonify({'error': 'Only admins can create shared categories'}), 403
    
    category = Category(
        name=data['name'],
        description=data['description'],
        is_shared=data['is_shared'],
        created_by=current_user_id
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify({
        'message': 'Category created successfully',
        'category': category.to_dict()
    }), 201

@categories_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    """Update a category."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    category = Category.query.get_or_404(category_id)
    
    if not category.can_modify(current_user_id, user.role):
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        schema = CategorySchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    # Check if new name conflicts with existing categories
    if data['name'] != category.name:
        existing = Category.query.filter_by(
            name=data['name'], 
            created_by=category.created_by
        ).first()
        
        if existing:
            return jsonify({'error': 'Category name already exists'}), 409
    
    # Only admins can modify shared status
    if data['is_shared'] != category.is_shared and not user.is_admin():
        return jsonify({'error': 'Only admins can modify shared status'}), 403
    
    # Update category
    category.name = data['name']
    category.description = data['description']
    category.is_shared = data['is_shared']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Category updated successfully',
        'category': category.to_dict()
    }), 200

@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    """Delete a category."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    category = Category.query.get_or_404(category_id)
    
    if not category.can_modify(current_user_id, user.role):
        return jsonify({'error': 'Permission denied'}), 403
    
    # Check if category has videos
    if category.videos.count() > 0:
        return jsonify({
            'error': 'Cannot delete category with videos. Move or delete videos first.'
        }), 409
    
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({'message': 'Category deleted successfully'}), 200

@categories_bp.route('/<int:category_id>/share', methods=['POST'])
@jwt_required()
def toggle_category_sharing(category_id):
    """Toggle category sharing status (admin only)."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    category = Category.query.get_or_404(category_id)
    
    data = request.get_json()
    is_shared = data.get('is_shared', not category.is_shared)
    
    category.is_shared = is_shared
    db.session.commit()
    
    action = 'shared' if is_shared else 'unshared'
    
    return jsonify({
        'message': f'Category {action} successfully',
        'category': category.to_dict()
    }), 200
