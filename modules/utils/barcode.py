"""
Barcode Utilities Module
Contains functions for barcode and QR code generation
"""

import barcode
from barcode.writer import ImageWriter
import qrcode
from PIL import Image
import io
import base64
import os
from datetime import datetime

def generate_asset_code(category_code, branch_id):
    """
    Generate unique asset code based on category and branch
    Format: CAT-BR001-YYYY-NNNN
    """
    year = datetime.now().year
    
    # This would typically query the database for the next sequence number
    # For now, we'll use a placeholder
    sequence = 1  # This should be fetched from database
    
    return f"{category_code}-BR{branch_id:03d}-{year}-{sequence:04d}"

def generate_asset_barcode(asset_code=None, category_code=None, branch_id=None):
    """
    Generate a barcode for an asset
    If asset_code is provided, use it directly
    Otherwise, generate from category_code and branch_id
    """
    if not asset_code:
        if not category_code or not branch_id:
            raise ValueError("Either asset_code or both category_code and branch_id must be provided")
        asset_code = generate_asset_code(category_code, branch_id)
    
    return asset_code

def create_barcode_image(code, format='CODE128'):
    """
    Create a barcode image
    
    Args:
        code (str): The code to encode
        format (str): Barcode format (CODE128, CODE39, EAN13, etc.)
    
    Returns:
        dict: Contains image data and metadata
    """
    try:
        # Get barcode class
        barcode_class = barcode.get_barcode_class(format)
        
        # Create barcode
        code_instance = barcode_class(code, writer=ImageWriter())
        
        # Generate image in memory
        buffer = io.BytesIO()
        code_instance.write(buffer)
        buffer.seek(0)
        
        # Convert to base64 for API response
        image_data = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            'success': True,
            'image_data': image_data,
            'format': format,
            'code': code,
            'mime_type': 'image/png'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def save_barcode_image(code, filename, format='CODE128', save_path='uploads/barcodes'):
    """
    Save a barcode image to file
    
    Args:
        code (str): The code to encode
        filename (str): Filename (without extension)
        format (str): Barcode format
        save_path (str): Directory to save the file
    
    Returns:
        dict: Contains file path and metadata
    """
    try:
        # Ensure directory exists
        os.makedirs(save_path, exist_ok=True)
        
        # Get barcode class
        barcode_class = barcode.get_barcode_class(format)
        
        # Create barcode
        code_instance = barcode_class(code, writer=ImageWriter())
        
        # Full file path
        file_path = os.path.join(save_path, f"{filename}.png")
        
        # Save image
        code_instance.save(file_path[:-4])  # Remove .png as barcode library adds it
        
        return {
            'success': True,
            'file_path': file_path,
            'filename': f"{filename}.png",
            'format': format,
            'code': code
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def create_qr_code(data, size=(200, 200)):
    """
    Create a QR code image
    
    Args:
        data (str): Data to encode in QR code
        size (tuple): Image size (width, height)
    
    Returns:
        dict: Contains image data and metadata
    """
    try:
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize(size, Image.LANCZOS)
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        image_data = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            'success': True,
            'image_data': image_data,
            'format': 'QR',
            'data': data,
            'mime_type': 'image/png'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def save_qr_code(data, filename, size=(200, 200), save_path='uploads/qrcodes'):
    """
    Save a QR code image to file
    
    Args:
        data (str): Data to encode
        filename (str): Filename (without extension)
        size (tuple): Image size
        save_path (str): Directory to save the file
    
    Returns:
        dict: Contains file path and metadata
    """
    try:
        # Ensure directory exists
        os.makedirs(save_path, exist_ok=True)
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize(size, Image.LANCZOS)
        
        # Full file path
        file_path = os.path.join(save_path, f"{filename}.png")
        
        # Save image
        img.save(file_path)
        
        return {
            'success': True,
            'file_path': file_path,
            'filename': f"{filename}.png",
            'format': 'QR',
            'data': data
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def generate_asset_qr_data(asset):
    """
    Generate QR code data for an asset
    
    Args:
        asset: Asset model instance
    
    Returns:
        str: JSON string with asset data
    """
    import json
    
    qr_data = {
        'asset_id': asset.id,
        'asset_code': asset.asset_code,
        'name': asset.name_en,
        'category': asset.category.name_en if asset.category else None,
        'branch': asset.branch.name_en if asset.branch else None,
        'warehouse': asset.warehouse.name_en if asset.warehouse else None,
        'serial_number': asset.serial_number,
        'barcode': asset.barcode,
        'url': f'/assets/{asset.id}',  # URL to view asset details
        'generated_at': datetime.now().isoformat()
    }
    
    return json.dumps(qr_data)

def validate_barcode_format(format_name):
    """
    Validate if barcode format is supported
    
    Args:
        format_name (str): Barcode format name
    
    Returns:
        bool: True if supported, False otherwise
    """
    supported_formats = [
        'CODE128', 'CODE39', 'CODE93', 'EAN8', 'EAN13', 'EAN14',
        'GS1', 'GTIN', 'ISBN10', 'ISBN13', 'ISSN', 'JAN',
        'PZN', 'UPC', 'UPCA'
    ]
    
    return format_name.upper() in supported_formats

def batch_generate_barcodes(codes, format='CODE128'):
    """
    Generate multiple barcodes at once
    
    Args:
        codes (list): List of codes to generate barcodes for
        format (str): Barcode format
    
    Returns:
        list: List of barcode generation results
    """
    results = []
    
    for code in codes:
        result = create_barcode_image(code, format)
        results.append(result)
    
    return results
