import os
import mimetypes
from werkzeug.utils import secure_filename

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed."""
    if not filename:
        return False
    
    extension = get_file_extension(filename).lower()
    return extension in allowed_extensions

def get_file_extension(filename):
    """Get file extension without the dot."""
    if not filename or '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[1].lower()

def get_mime_type(filename):
    """Get MIME type of file."""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'

def sanitize_filename(filename):
    """Sanitize filename for safe storage."""
    if not filename:
        return 'unnamed'
    
    # Use werkzeug's secure_filename
    safe_name = secure_filename(filename)
    
    # If secure_filename returns empty string, use fallback
    if not safe_name:
        extension = get_file_extension(filename)
        safe_name = f"unnamed.{extension}" if extension else "unnamed"
    
    return safe_name

def format_file_size(size_bytes):
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def ensure_directory_exists(directory_path):
    """Ensure directory exists, create if it doesn't."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)
    return directory_path

def get_safe_path(base_path, filename):
    """Get safe file path preventing directory traversal."""
    # Sanitize filename
    safe_filename = sanitize_filename(filename)
    
    # Join with base path
    full_path = os.path.join(base_path, safe_filename)
    
    # Resolve any relative path components
    full_path = os.path.abspath(full_path)
    base_path = os.path.abspath(base_path)
    
    # Ensure the path is within the base directory
    if not full_path.startswith(base_path):
        raise ValueError("Invalid file path")
    
    return full_path

def cleanup_file(file_path):
    """Safely delete a file if it exists."""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            return True
    except OSError:
        pass
    return False

def get_directory_size(directory_path):
    """Get total size of directory in bytes."""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(directory_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
    except OSError:
        pass
    return total_size

def validate_upload_path(file_path, allowed_base_paths):
    """Validate that file path is within allowed directories."""
    abs_file_path = os.path.abspath(file_path)
    
    for base_path in allowed_base_paths:
        abs_base_path = os.path.abspath(base_path)
        if abs_file_path.startswith(abs_base_path):
            return True
    
    return False

class FileUploadError(Exception):
    """Custom exception for file upload errors."""
    pass

class FileValidationError(Exception):
    """Custom exception for file validation errors."""
    pass
