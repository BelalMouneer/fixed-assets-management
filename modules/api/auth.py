"""
Authentication API Module
Handles user authentication, registration, and JWT token management
"""

from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from modules.app import Session
from modules.models.models import User, Permission
from modules.utils.auth import validate_password_strength, hash_password
from modules.utils.permissions import require_permission
import datetime

# Create namespace
auth_ns = Namespace('auth', description='Authentication operations')

# API Models for documentation
login_model = auth_ns.model('Login', {
    'username': fields.String(required=True, description='Username or email'),
    'password': fields.String(required=True, description='Password')
})

register_model = auth_ns.model('Register', {
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(required=True, description='Email address'),
    'password': fields.String(required=True, description='Password'),
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='Last name'),
    'phone': fields.String(required=False, description='Phone number'),
    'position_id': fields.Integer(required=True, description='Position ID'),
    'branch_id': fields.Integer(required=True, description='Branch ID'),
    'employee_id': fields.String(required=False, description='Employee ID')
})

change_password_model = auth_ns.model('ChangePassword', {
    'old_password': fields.String(required=True, description='Current password'),
    'new_password': fields.String(required=True, description='New password')
})

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.doc('user_login')
    def post(self):
        """User login"""
        try:
            data = request.get_json()
            username_or_email = data.get('username')
            password = data.get('password')
            
            if not username_or_email or not password:
                return {'message': 'Username and password are required'}, 400
            
            session = Session()
            
            # Find user by username or email
            user = session.query(User).filter(
                (User.username == username_or_email) | 
                (User.email == username_or_email)
            ).first()
            
            if not user or not user.check_password(password):
                return {'message': 'Invalid credentials'}, 401
            
            if user.status != 'ACTIVE':
                return {'message': 'Account is not active'}, 403
            
            # Update last login
            user.last_login = datetime.datetime.utcnow()
            session.commit()
            
            # Create tokens
            access_token = create_access_token(
                identity=user.id,
                expires_delta=datetime.timedelta(hours=24)
            )
            refresh_token = create_refresh_token(identity=user.id)
            
            # Get user permissions
            permissions = []
            for perm in user.permissions:
                if perm.is_active:
                    permissions.append(perm.code)
            
            # Get position permissions
            if user.position:
                for perm in user.position.permissions:
                    if perm.is_active and perm.code not in permissions:
                        permissions.append(perm.code)
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict(),
                'permissions': permissions
            }, 200
            
        except Exception as e:
            return {'message': f'Login failed: {str(e)}'}, 500
        finally:
            session.close()

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_model)
    @auth_ns.doc('user_register')
    @jwt_required()
    @require_permission('manage_users')
    def post(self):
        """Register a new user (admin only)"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'position_id', 'branch_id']
            for field in required_fields:
                if not data.get(field):
                    return {'message': f'{field} is required'}, 400
            
            # Validate password strength
            password_validation = validate_password_strength(data['password'])
            if not password_validation['is_valid']:
                return {'message': password_validation['message']}, 400
            
            session = Session()
            
            # Check if username or email already exists
            existing_user = session.query(User).filter(
                (User.username == data['username']) | 
                (User.email == data['email'])
            ).first()
            
            if existing_user:
                return {'message': 'Username or email already exists'}, 409
            
            # Create new user
            new_user = User(
                username=data['username'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone=data.get('phone'),
                position_id=data['position_id'],
                branch_id=data['branch_id'],
                employee_id=data.get('employee_id'),
                created_by=get_jwt_identity()
            )
            
            new_user.set_password(data['password'])
            
            session.add(new_user)
            session.commit()
            
            return {
                'message': 'User registered successfully',
                'user': new_user.to_dict()
            }, 201
            
        except Exception as e:
            session.rollback()
            return {'message': f'Registration failed: {str(e)}'}, 500
        finally:
            session.close()

@auth_ns.route('/refresh')
class RefreshToken(Resource):
    @auth_ns.doc('refresh_token')
    @jwt_required(refresh=True)
    def post(self):
        """Refresh access token"""
        try:
            current_user_id = get_jwt_identity()
            
            session = Session()
            user = session.query(User).get(current_user_id)
            
            if not user or user.status != 'ACTIVE':
                return {'message': 'User not found or inactive'}, 404
            
            new_token = create_access_token(
                identity=current_user_id,
                expires_delta=datetime.timedelta(hours=24)
            )
            
            return {'access_token': new_token}, 200
            
        except Exception as e:
            return {'message': f'Token refresh failed: {str(e)}'}, 500
        finally:
            session.close()

@auth_ns.route('/me')
class Me(Resource):
    @auth_ns.doc('get_current_user')
    @jwt_required()
    def get(self):
        """Get current user information"""
        try:
            current_user_id = get_jwt_identity()
            
            session = Session()
            user = session.query(User).get(current_user_id)
            
            if not user:
                return {'message': 'User not found'}, 404
            
            # Get user permissions
            permissions = []
            for perm in user.permissions:
                if perm.is_active:
                    permissions.append(perm.code)
            
            # Get position permissions
            if user.position:
                for perm in user.position.permissions:
                    if perm.is_active and perm.code not in permissions:
                        permissions.append(perm.code)
            
            user_data = user.to_dict(include_sensitive=True)
            user_data['permissions'] = permissions
            
            return user_data, 200
            
        except Exception as e:
            return {'message': f'Failed to get user info: {str(e)}'}, 500
        finally:
            session.close()

@auth_ns.route('/change-password')
class ChangePassword(Resource):
    @auth_ns.expect(change_password_model)
    @auth_ns.doc('change_password')
    @jwt_required()
    def post(self):
        """Change user password"""
        try:
            data = request.get_json()
            current_user_id = get_jwt_identity()
            
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            
            if not old_password or not new_password:
                return {'message': 'Both old and new passwords are required'}, 400
            
            # Validate new password strength
            password_validation = validate_password_strength(new_password)
            if not password_validation['is_valid']:
                return {'message': password_validation['message']}, 400
            
            session = Session()
            user = session.query(User).get(current_user_id)
            
            if not user:
                return {'message': 'User not found'}, 404
            
            # Verify old password
            if not user.check_password(old_password):
                return {'message': 'Invalid current password'}, 400
            
            # Update password
            user.set_password(new_password)
            session.commit()
            
            return {'message': 'Password changed successfully'}, 200
            
        except Exception as e:
            session.rollback()
            return {'message': f'Password change failed: {str(e)}'}, 500
        finally:
            session.close()

@auth_ns.route('/logout')
class Logout(Resource):
    @auth_ns.doc('user_logout')
    @jwt_required()
    def post(self):
        """User logout (token blacklisting would be implemented here)"""
        # In a production environment, you would blacklist the token
        # For now, just return success
        return {'message': 'Logged out successfully'}, 200
