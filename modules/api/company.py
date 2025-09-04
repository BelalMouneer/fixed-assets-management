"""
Company API Module
Handles company information management
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from modules.app import Session
from modules.models.models import Company
from modules.utils.permissions import require_permission
import datetime

# Create namespace
company_ns = Namespace('companies', description='Company management operations')

# API Models for documentation
company_model = company_ns.model('Company', {
    'name_en': fields.String(required=True, description='Company name in English'),
    'name_ar': fields.String(required=True, description='Company name in Arabic'),
    'address_en': fields.String(required=False, description='Address in English'),
    'address_ar': fields.String(required=False, description='Address in Arabic'),
    'phone': fields.String(required=False, description='Phone number'),
    'email': fields.String(required=False, description='Email address'),
    'commercial_registry': fields.String(required=False, description='Commercial registry number'),
    'tax_number': fields.String(required=False, description='Tax number'),
    'website': fields.String(required=False, description='Website URL'),
    'logo_path': fields.String(required=False, description='Logo file path')
})

@company_ns.route('')
class CompanyList(Resource):
    @company_ns.doc('list_companies')
    @jwt_required()
    @require_permission('view_company')
    def get(self):
        """Get all companies"""
        try:
            session = Session()
            companies = session.query(Company).filter(Company.is_active == True).all()
            
            return {
                'companies': [company.to_dict() for company in companies],
                'total': len(companies)
            }, 200
            
        except Exception as e:
            return {'message': f'Failed to retrieve companies: {str(e)}'}, 500
        finally:
            session.close()
    
    @company_ns.expect(company_model)
    @company_ns.doc('create_company')
    @jwt_required()
    @require_permission('manage_company')
    def post(self):
        """Create a new company"""
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data.get('name_en') or not data.get('name_ar'):
                return {'message': 'Company name in English and Arabic are required'}, 400
            
            session = Session()
            
            # Check for duplicate commercial registry or tax number
            if data.get('commercial_registry'):
                existing = session.query(Company).filter(
                    Company.commercial_registry == data['commercial_registry']
                ).first()
                if existing:
                    return {'message': 'Commercial registry number already exists'}, 409
            
            if data.get('tax_number'):
                existing = session.query(Company).filter(
                    Company.tax_number == data['tax_number']
                ).first()
                if existing:
                    return {'message': 'Tax number already exists'}, 409
            
            # Create new company
            company = Company(
                name_en=data['name_en'],
                name_ar=data['name_ar'],
                address_en=data.get('address_en'),
                address_ar=data.get('address_ar'),
                phone=data.get('phone'),
                email=data.get('email'),
                commercial_registry=data.get('commercial_registry'),
                tax_number=data.get('tax_number'),
                website=data.get('website'),
                logo_path=data.get('logo_path')
            )
            
            session.add(company)
            session.commit()
            
            return {
                'message': 'Company created successfully',
                'company': company.to_dict()
            }, 201
            
        except Exception as e:
            session.rollback()
            return {'message': f'Failed to create company: {str(e)}'}, 500
        finally:
            session.close()

@company_ns.route('/<int:company_id>')
class CompanyDetail(Resource):
    @company_ns.doc('get_company')
    @jwt_required()
    @require_permission('view_company')
    def get(self, company_id):
        """Get a specific company"""
        try:
            session = Session()
            company = session.query(Company).filter(
                Company.id == company_id,
                Company.is_active == True
            ).first()
            
            if not company:
                return {'message': 'Company not found'}, 404
            
            return company.to_dict(), 200
            
        except Exception as e:
            return {'message': f'Failed to retrieve company: {str(e)}'}, 500
        finally:
            session.close()
    
    @company_ns.expect(company_model)
    @company_ns.doc('update_company')
    @jwt_required()
    @require_permission('manage_company')
    def put(self, company_id):
        """Update a company"""
        try:
            data = request.get_json()
            
            session = Session()
            company = session.query(Company).filter(
                Company.id == company_id,
                Company.is_active == True
            ).first()
            
            if not company:
                return {'message': 'Company not found'}, 404
            
            # Check for duplicate commercial registry or tax number (excluding current company)
            if data.get('commercial_registry') and data['commercial_registry'] != company.commercial_registry:
                existing = session.query(Company).filter(
                    Company.commercial_registry == data['commercial_registry'],
                    Company.id != company_id
                ).first()
                if existing:
                    return {'message': 'Commercial registry number already exists'}, 409
            
            if data.get('tax_number') and data['tax_number'] != company.tax_number:
                existing = session.query(Company).filter(
                    Company.tax_number == data['tax_number'],
                    Company.id != company_id
                ).first()
                if existing:
                    return {'message': 'Tax number already exists'}, 409
            
            # Update company fields
            if data.get('name_en'):
                company.name_en = data['name_en']
            if data.get('name_ar'):
                company.name_ar = data['name_ar']
            if 'address_en' in data:
                company.address_en = data['address_en']
            if 'address_ar' in data:
                company.address_ar = data['address_ar']
            if 'phone' in data:
                company.phone = data['phone']
            if 'email' in data:
                company.email = data['email']
            if 'commercial_registry' in data:
                company.commercial_registry = data['commercial_registry']
            if 'tax_number' in data:
                company.tax_number = data['tax_number']
            if 'website' in data:
                company.website = data['website']
            if 'logo_path' in data:
                company.logo_path = data['logo_path']
            
            company.updated_at = datetime.datetime.utcnow()
            session.commit()
            
            return {
                'message': 'Company updated successfully',
                'company': company.to_dict()
            }, 200
            
        except Exception as e:
            session.rollback()
            return {'message': f'Failed to update company: {str(e)}'}, 500
        finally:
            session.close()
    
    @company_ns.doc('delete_company')
    @jwt_required()
    @require_permission('manage_company')
    def delete(self, company_id):
        """Soft delete a company"""
        try:
            session = Session()
            company = session.query(Company).filter(
                Company.id == company_id,
                Company.is_active == True
            ).first()
            
            if not company:
                return {'message': 'Company not found'}, 404
            
            # Check if company has active branches
            if company.branches:
                active_branches = [b for b in company.branches if b.is_active]
                if active_branches:
                    return {
                        'message': 'Cannot delete company with active branches. Please deactivate branches first.'
                    }, 400
            
            # Soft delete
            company.is_active = False
            company.updated_at = datetime.datetime.utcnow()
            session.commit()
            
            return {'message': 'Company deleted successfully'}, 200
            
        except Exception as e:
            session.rollback()
            return {'message': f'Failed to delete company: {str(e)}'}, 500
        finally:
            session.close()
