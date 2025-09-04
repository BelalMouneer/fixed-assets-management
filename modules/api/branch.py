"""
Branch API Module
Handles branch management
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from modules.app import Session
from modules.models.models import Branch, Company
from modules.utils.permissions import require_permission
import datetime

# Create namespace
branch_ns = Namespace('branches', description='Branch management operations')

# API Models
branch_model = branch_ns.model('Branch', {
    'company_id': fields.Integer(required=True, description='Company ID'),
    'name_en': fields.String(required=True, description='Branch name in English'),
    'name_ar': fields.String(required=True, description='Branch name in Arabic'),
    'address_en': fields.String(required=False, description='Address in English'),
    'address_ar': fields.String(required=False, description='Address in Arabic'),
    'phone': fields.String(required=False, description='Phone number'),
    'email': fields.String(required=False, description='Email address'),
    'manager_name': fields.String(required=False, description='Branch manager name')
})

@branch_ns.route('')
class BranchList(Resource):
    @branch_ns.doc('list_branches')
    @jwt_required()
    @require_permission('view_branches')
    def get(self):
        """Get all branches"""
        try:
            company_id = request.args.get('company_id', type=int)
            
            session = Session()
            query = session.query(Branch).filter(Branch.is_active == True)
            
            if company_id:
                query = query.filter(Branch.company_id == company_id)
            
            branches = query.all()
            
            return {
                'branches': [branch.to_dict() for branch in branches],
                'total': len(branches)
            }, 200
            
        except Exception as e:
            return {'message': f'Failed to retrieve branches: {str(e)}'}, 500
        finally:
            session.close()
    
    @branch_ns.expect(branch_model)
    @branch_ns.doc('create_branch')
    @jwt_required()
    @require_permission('manage_branches')
    def post(self):
        """Create a new branch"""
        try:
            data = request.get_json()
            
            if not data.get('name_en') or not data.get('name_ar') or not data.get('company_id'):
                return {'message': 'Branch name (EN/AR) and company ID are required'}, 400
            
            session = Session()
            
            # Verify company exists
            company = session.query(Company).get(data['company_id'])
            if not company or not company.is_active:
                return {'message': 'Invalid company ID'}, 400
            
            branch = Branch(
                company_id=data['company_id'],
                name_en=data['name_en'],
                name_ar=data['name_ar'],
                address_en=data.get('address_en'),
                address_ar=data.get('address_ar'),
                phone=data.get('phone'),
                email=data.get('email'),
                manager_name=data.get('manager_name')
            )
            
            session.add(branch)
            session.commit()
            
            return {
                'message': 'Branch created successfully',
                'branch': branch.to_dict()
            }, 201
            
        except Exception as e:
            session.rollback()
            return {'message': f'Failed to create branch: {str(e)}'}, 500
        finally:
            session.close()

@branch_ns.route('/<int:branch_id>')
class BranchDetail(Resource):
    @branch_ns.doc('get_branch')
    @jwt_required()
    @require_permission('view_branches')
    def get(self, branch_id):
        """Get a specific branch"""
        try:
            session = Session()
            branch = session.query(Branch).filter(
                Branch.id == branch_id,
                Branch.is_active == True
            ).first()
            
            if not branch:
                return {'message': 'Branch not found'}, 404
            
            return branch.to_dict(), 200
            
        except Exception as e:
            return {'message': f'Failed to retrieve branch: {str(e)}'}, 500
        finally:
            session.close()
    
    @branch_ns.expect(branch_model)
    @branch_ns.doc('update_branch')
    @jwt_required()
    @require_permission('manage_branches')
    def put(self, branch_id):
        """Update a branch"""
        try:
            data = request.get_json()
            
            session = Session()
            branch = session.query(Branch).filter(
                Branch.id == branch_id,
                Branch.is_active == True
            ).first()
            
            if not branch:
                return {'message': 'Branch not found'}, 404
            
            # Update fields
            updateable_fields = ['name_en', 'name_ar', 'address_en', 'address_ar', 'phone', 'email', 'manager_name']
            for field in updateable_fields:
                if field in data:
                    setattr(branch, field, data[field])
            
            branch.updated_at = datetime.datetime.utcnow()
            session.commit()
            
            return {
                'message': 'Branch updated successfully',
                'branch': branch.to_dict()
            }, 200
            
        except Exception as e:
            session.rollback()
            return {'message': f'Failed to update branch: {str(e)}'}, 500
        finally:
            session.close()
    
    @branch_ns.doc('delete_branch')
    @jwt_required()
    @require_permission('manage_branches')
    def delete(self, branch_id):
        """Soft delete a branch"""
        try:
            session = Session()
            branch = session.query(Branch).filter(
                Branch.id == branch_id,
                Branch.is_active == True
            ).first()
            
            if not branch:
                return {'message': 'Branch not found'}, 404
            
            # Check for dependencies
            if branch.warehouses or branch.users or branch.assets:
                return {
                    'message': 'Cannot delete branch with associated warehouses, users, or assets'
                }, 400
            
            branch.is_active = False
            branch.updated_at = datetime.datetime.utcnow()
            session.commit()
            
            return {'message': 'Branch deleted successfully'}, 200
            
        except Exception as e:
            session.rollback()
            return {'message': f'Failed to delete branch: {str(e)}'}, 500
        finally:
            session.close()
