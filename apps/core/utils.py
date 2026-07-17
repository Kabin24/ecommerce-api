"""
Utilities and helpers for core app.
"""
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO


def validate_image_file(file, max_size_mb=5, allowed_extensions=None):
    """
    Validate image file size and format.
    
    Args:
        file: The uploaded file
        max_size_mb: Maximum file size in MB (default: 5)
        allowed_extensions: List of allowed file extensions (default: ['jpg', 'jpeg', 'png', 'webp'])
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if allowed_extensions is None:
        allowed_extensions = ['jpg', 'jpeg', 'png', 'webp']
    
    # Check file size
    file_size_mb = file.size / (1024 * 1024)
    if file_size_mb > max_size_mb:
        return False, f'File size must be less than {max_size_mb}MB. Current size: {file_size_mb:.2f}MB'
    
    # Check file extension
    file_ext = file.name.split('.')[-1].lower()
    if file_ext not in allowed_extensions:
        return False, f'Invalid file format. Allowed formats: {", ".join(allowed_extensions)}'
    
    # Verify it's actually an image
    try:
        img = Image.open(file)
        img.verify()
    except Exception as e:
        return False, f'Invalid image file: {str(e)}'
    
    return True, None


def resize_image(image_file, width=None, height=None, max_width=2000, max_height=2000):
    """
    Resize image to fit within max dimensions while maintaining aspect ratio.
    
    Args:
        image_file: The uploaded image file
        width: Target width (optional, will use aspect ratio)
        height: Target height (optional, will use aspect ratio)
        max_width: Maximum width allowed
        max_height: Maximum height allowed
    
    Returns:
        ContentFile: Resized image file
    """
    img = Image.open(image_file)
    
    # Calculate dimensions if not provided
    if width is None and height is None:
        width, height = img.size
        # Scale down if larger than max
        if width > max_width or height > max_height:
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    else:
        if width and not height:
            # Maintain aspect ratio using width
            wpercent = width / float(img.size[0])
            hsize = int(float(img.size[1]) * float(wpercent))
            img = img.resize((width, hsize), Image.Resampling.LANCZOS)
        elif height and not width:
            # Maintain aspect ratio using height
            hpercent = height / float(img.size[1])
            wsize = int(float(img.size[0]) * float(hpercent))
            img = img.resize((wsize, height), Image.Resampling.LANCZOS)
        else:
            # Both provided, resize to exact dimensions
            img = img.resize((width, height), Image.Resampling.LANCZOS)
    
    # Save resized image
    output = BytesIO()
    img.save(output, format='JPEG', quality=85, optimize=True)
    output.seek(0)
    
    return ContentFile(output.getvalue(), name=image_file.name)
