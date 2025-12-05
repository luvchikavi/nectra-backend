"""
Security utilities for Nectar application
- File upload validation
- Input sanitization
"""

import os
import magic
from django.conf import settings


# Allowed file types for different upload categories
ALLOWED_FILE_TYPES = {
    'excel': {
        'extensions': ['.xlsx', '.xls'],
        'mime_types': [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
        ]
    },
    'document': {
        'extensions': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.rtf'],
        'mime_types': [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/plain',
            'application/rtf',
        ]
    },
    'image': {
        'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
        'mime_types': [
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/bmp',
        ]
    }
}

# Maximum file sizes (in bytes)
MAX_FILE_SIZES = {
    'excel': 10 * 1024 * 1024,      # 10 MB
    'document': 50 * 1024 * 1024,   # 50 MB
    'image': 5 * 1024 * 1024,       # 5 MB
    'default': 10 * 1024 * 1024,    # 10 MB default
}

# Dangerous file extensions that should NEVER be allowed
DANGEROUS_EXTENSIONS = [
    '.exe', '.bat', '.cmd', '.sh', '.ps1', '.vbs', '.js',
    '.jar', '.msi', '.dll', '.scr', '.com', '.pif', '.hta',
    '.php', '.py', '.rb', '.pl', '.cgi', '.asp', '.aspx', '.jsp'
]


class FileValidationError(Exception):
    """Custom exception for file validation errors"""
    pass


def validate_file_upload(uploaded_file, category='document'):
    """
    Validate an uploaded file for security

    Args:
        uploaded_file: Django UploadedFile object
        category: 'excel', 'document', or 'image'

    Returns:
        dict with validation results

    Raises:
        FileValidationError if validation fails
    """
    if uploaded_file is None:
        raise FileValidationError("No file provided")

    filename = uploaded_file.name
    file_ext = os.path.splitext(filename)[1].lower()

    # 1. Check for dangerous extensions
    if file_ext in DANGEROUS_EXTENSIONS:
        raise FileValidationError(f"File type '{file_ext}' is not allowed for security reasons")

    # 2. Check file size
    max_size = MAX_FILE_SIZES.get(category, MAX_FILE_SIZES['default'])
    if uploaded_file.size > max_size:
        max_mb = max_size / (1024 * 1024)
        raise FileValidationError(f"File size exceeds maximum allowed ({max_mb:.0f} MB)")

    # 3. Check extension against allowed list
    allowed = ALLOWED_FILE_TYPES.get(category)
    if allowed:
        if file_ext not in allowed['extensions']:
            raise FileValidationError(
                f"File extension '{file_ext}' not allowed. "
                f"Allowed types: {', '.join(allowed['extensions'])}"
            )

    # 4. Verify MIME type using python-magic (checks actual file content)
    try:
        # Read first chunk to detect MIME type
        uploaded_file.seek(0)
        file_header = uploaded_file.read(2048)
        uploaded_file.seek(0)  # Reset file position

        detected_mime = magic.from_buffer(file_header, mime=True)

        if allowed and detected_mime not in allowed['mime_types']:
            # Some Excel files have generic MIME types, be lenient
            if category == 'excel' and 'zip' in detected_mime:
                pass  # xlsx files are zip archives, this is OK
            else:
                raise FileValidationError(
                    f"File content type '{detected_mime}' doesn't match expected type"
                )
    except ImportError:
        # python-magic not installed, skip MIME validation
        pass
    except Exception as e:
        # Log but don't fail if MIME detection has issues
        print(f"Warning: MIME type validation skipped: {e}")

    # 5. Sanitize filename (remove path traversal attempts)
    safe_filename = os.path.basename(filename)
    safe_filename = "".join(c for c in safe_filename if c.isalnum() or c in '._-')

    return {
        'valid': True,
        'filename': filename,
        'safe_filename': safe_filename,
        'extension': file_ext,
        'size': uploaded_file.size,
        'category': category
    }


def sanitize_filename(filename):
    """
    Sanitize a filename to prevent path traversal and other attacks
    """
    # Get just the filename without path
    filename = os.path.basename(filename)

    # Remove any null bytes
    filename = filename.replace('\x00', '')

    # Keep only safe characters
    safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-')
    filename = ''.join(c if c in safe_chars else '_' for c in filename)

    # Ensure it doesn't start with a dot (hidden file)
    if filename.startswith('.'):
        filename = '_' + filename[1:]

    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255 - len(ext)] + ext

    return filename or 'unnamed_file'
