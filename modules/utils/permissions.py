"""
Permissions Utilities Module
Contains decorators and helper functions for role-based access control
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from modules.app import Session
from modules.models.models import User

def require_permission(permission_code):
    """
    Decorator to require specific permission for accessing an endpoint
    
    Args:
        permission_code (str): The permission code required (e.g., 'manage_users', 'view_assets')
    
    Returns:
        decorator function
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                current_user_id = get_jwt_identity()
                
                session = Session()
                user = session.query(User).get(current_user_id)
                
                if not user:
                    return {'message': 'User not found'}, 404
                
                if not user.has_permission(permission_code):
                    return {
                        'message': f'Access denied. Required permission: {permission_code}'
                    }, 403
                
                return f(*args, **kwargs)
                
            except Exception as e:
                return {'message': f'Permission check failed: {str(e)}'}, 500
            finally:
                session.close()
        
        return decorated_function
    return decorator

def require_any_permission(*permission_codes):
    """
    Decorator to require any of the specified permissions for accessing an endpoint
    
    Args:
        *permission_codes: Multiple permission codes, user needs at least one
    
    Returns:
        decorator function
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                current_user_id = get_jwt_identity()
                
                session = Session()
                user = session.query(User).get(current_user_id)
                
                if not user:
                    return {'message': 'User not found'}, 404
                
                has_any_permission = any(user.has_permission(code) for code in permission_codes)
                
                if not has_any_permission:
                    return {
                        'message': f'Access denied. Required permissions (any): {", ".join(permission_codes)}'
                    }, 403
                
                return f(*args, **kwargs)
                
            except Exception as e:
                return {'message': f'Permission check failed: {str(e)}'}, 500
            finally:
                session.close()
        
        return decorated_function
    return decorator

def require_all_permissions(*permission_codes):
    """
    Decorator to require all of the specified permissions for accessing an endpoint
    
    Args:
        *permission_codes: Multiple permission codes, user needs all of them
    
    Returns:
        decorator function
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                current_user_id = get_jwt_identity()
                
                session = Session()
                user = session.query(User).get(current_user_id)
                
                if not user:
                    return {'message': 'User not found'}, 404
                
                has_all_permissions = all(user.has_permission(code) for code in permission_codes)
                
                if not has_all_permissions:
                    return {
                        'message': f'Access denied. Required permissions (all): {", ".join(permission_codes)}'
                    }, 403
                
                return f(*args, **kwargs)
                
            except Exception as e:
                return {'message': f'Permission check failed: {str(e)}'}, 500
            finally:
                session.close()
        
        return decorated_function
    return decorator

def check_user_permission(user_id, permission_code):
    """
    Check if a user has a specific permission
    
    Args:
        user_id (int): User ID
        permission_code (str): Permission code to check
    
    Returns:
        bool: True if user has permission, False otherwise
    """
    try:
        session = Session()
        user = session.query(User).get(user_id)
        
        if not user:
            return False
        
        return user.has_permission(permission_code)
        
    except Exception:
        return False
    finally:
        session.close()

def get_user_permissions(user_id):
    """
    Get all permissions for a user (direct and from position)
    
    Args:
        user_id (int): User ID
    
    Returns:
        list: List of permission codes
    """
    try:
        session = Session()
        user = session.query(User).get(user_id)
        
        if not user:
            return []
        
        permissions = []
        
        # Direct permissions
        for perm in user.permissions:
            if perm.is_active:
                permissions.append(perm.code)
        
        # Position permissions
        if user.position:
            for perm in user.position.permissions:
                if perm.is_active and perm.code not in permissions:
                    permissions.append(perm.code)
        
        return permissions
        
    except Exception:
        return []
    finally:
        session.close()

# Common permission codes used in the system
PERMISSIONS = {
    # Company management
    'manage_company': 'Manage company information',
    'view_company': 'View company information',
    
    # Branch management  
    'manage_branches': 'Manage branches',
    'view_branches': 'View branches',
    
    # Warehouse management
    'manage_warehouses': 'Manage warehouses',
    'view_warehouses': 'View warehouses',
    
    # User management
    'manage_users': 'Manage users',
    'view_users': 'View users',
    'reset_user_passwords': 'Reset user passwords',
    
    # Position management
    'manage_positions': 'Manage positions/roles',
    'view_positions': 'View positions/roles',
    
    # Permission management
    'manage_permissions': 'Manage permissions',
    'view_permissions': 'View permissions',
    
    # Asset management
    'manage_assets': 'Manage assets',
    'view_assets': 'View assets',
    'delete_assets': 'Delete assets',
    'transfer_assets': 'Transfer assets between locations',
    
    # Asset categories
    'manage_asset_categories': 'Manage asset categories',
    'view_asset_categories': 'View asset categories',
    
    # Asset maintenance
    'manage_maintenance': 'Manage asset maintenance',
    'view_maintenance': 'View asset maintenance records',
    
    # Reports
    'generate_reports': 'Generate reports',
    'view_financial_reports': 'View financial reports',
    'export_data': 'Export data',
    
    # Barcode system
    'generate_barcodes': 'Generate and print barcodes',
    'scan_barcodes': 'Scan barcodes',
    
    # File management
    'upload_files': 'Upload files and attachments',
    'delete_files': 'Delete files and attachments',
    
    # System administration
    'system_admin': 'System administration access',
    'view_audit_logs': 'View audit logs',
    'manage_system_settings': 'Manage system settings',
}
