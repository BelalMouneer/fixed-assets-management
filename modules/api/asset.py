"""
Asset API Module
Handles fixed assets management
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from modules.app import Session
from modules.models.models import Asset, AssetCategory, Branch, Warehouse, User
from modules.utils.permissions import require_permission
from modules.utils.barcode import generate_asset_barcode
import datetime

# Create namespace
asset_ns = Namespace('assets', description='Asset management operations')

# API Models for documentation
asset_model = asset_ns.model('Asset', {
    'name_en': fields.String(required=True, description='Asset name in English'),
    'name_ar': fields.String(required=True, description='Asset name in Arabic'),
    'description': fields.String(required=False, description='Asset description'),
    'category_id': fields.Integer(required=True, description='Asset category ID'),
    'branch_id': fields.Integer(required=True, description='Branch ID'),
    'warehouse_id': fields.Integer(required=True, description='Warehouse ID'),
    'purchase_date': fields.String(required=True, description='Purchase date (YYYY-MM-DD)'),
    'purchase_value': fields.Float(required=True, description='Purchase value'),
    'invoice_number': fields.String(required=False, description='Invoice number'),
    'supplier_name': fields.String(required=False, description='Supplier name'),
    'warranty_start_date': fields.String(required=False, description='Warranty start date (YYYY-MM-DD)'),
    'warranty_end_date': fields.String(required=False, description='Warranty end date (YYYY-MM-DD)'),
    'quantity': fields.Integer(required=False, description='Quantity (default: 1)'),
    'unit': fields.String(required=False, description='Unit of measurement'),
    'serial_number': fields.String(required=False, description='Serial number'),
    'model': fields.String(required=False, description='Model'),
    'manufacturer': fields.String(required=False, description='Manufacturer'),
    'location_notes': fields.String(required=False, description='Location notes'),
    'rfid_tag': fields.String(required=False, description='RFID tag')
})

asset_search_model = asset_ns.model('AssetSearch', {
    'search': fields.String(required=False, description='Search term'),
    'category_id': fields.Integer(required=False, description='Filter by category'),
    'branch_id': fields.Integer(required=False, description='Filter by branch'),
    'warehouse_id': fields.Integer(required=False, description='Filter by warehouse'),
    'status': fields.String(required=False, description='Filter by status'),
    'page': fields.Integer(required=False, description='Page number (default: 1)'),
    'per_page': fields.Integer(required=False, description='Items per page (default: 20)')
})

@asset_ns.route('')
class AssetList(Resource):
    @asset_ns.doc('list_assets')
    @asset_ns.expect(asset_search_model)
    @jwt_required()
    @require_permission('view_assets')
    def get(self):
        """Get all assets with filtering and pagination"""
        try:
            # Get query parameters
            search = request.args.get('search', '')
            category_id = request.args.get('category_id', type=int)
            branch_id = request.args.get('branch_id', type=int)
            warehouse_id = request.args.get('warehouse_id', type=int)
            status = request.args.get('status', '')
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 20, type=int), 100)  # Max 100 per page
            
            session = Session()
            
            # Build query
            query = session.query(Asset)
            
            # Apply filters
            if search:
                query = query.filter(
                    (Asset.name_en.ilike(f'%{search}%')) |
                    (Asset.name_ar.ilike(f'%{search}%')) |
                    (Asset.asset_code.ilike(f'%{search}%')) |
                    (Asset.serial_number.ilike(f'%{search}%')) |
                    (Asset.barcode.ilike(f'%{search}%'))
                )
            
            if category_id:
                query = query.filter(Asset.category_id == category_id)
            
            if branch_id:
                query = query.filter(Asset.branch_id == branch_id)
            
            if warehouse_id:
                query = query.filter(Asset.warehouse_id == warehouse_id)
            
            if status:
                query = query.filter(Asset.status == status)
            
            # Get total count before pagination
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * per_page
            assets = query.offset(offset).limit(per_page).all()
            
            return {
                'assets': [asset.to_dict(include_relations=True) for asset in assets],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }, 200
            
        except Exception as e:
            return {'message': f'Failed to retrieve assets: {str(e)}'}, 500
        finally:
            session.close()
    
    @asset_ns.expect(asset_model)
    @asset_ns.doc('create_asset')
    @jwt_required()
    @require_permission('manage_assets')
    def post(self):
        """Create a new asset"""
        try:
            data = request.get_json()
            current_user_id = get_jwt_identity()
            
            # Validate required fields
            required_fields = ['name_en', 'name_ar', 'category_id', 'branch_id', 'warehouse_id', 'purchase_date', 'purchase_value']
            for field in required_fields:
                if not data.get(field):
                    return {'message': f'{field} is required'}, 400
            
            session = Session()
            
            # Validate references exist
            category = session.query(AssetCategory).get(data['category_id'])
            if not category or not category.is_active:
                return {'message': 'Invalid asset category'}, 400
            
            branch = session.query(Branch).get(data['branch_id'])
            if not branch or not branch.is_active:
                return {'message': 'Invalid branch'}, 400
            
            warehouse = session.query(Warehouse).get(data['warehouse_id'])
            if not warehouse or not warehouse.is_active or warehouse.branch_id != data['branch_id']:
                return {'message': 'Invalid warehouse or warehouse does not belong to selected branch'}, 400
            
            # Parse dates
            try:
                purchase_date = datetime.datetime.strptime(data['purchase_date'], '%Y-%m-%d').date()
                warranty_start_date = None
                warranty_end_date = None
                
                if data.get('warranty_start_date'):
                    warranty_start_date = datetime.datetime.strptime(data['warranty_start_date'], '%Y-%m-%d').date()
                
                if data.get('warranty_end_date'):
                    warranty_end_date = datetime.datetime.strptime(data['warranty_end_date'], '%Y-%m-%d').date()
                    
            except ValueError as e:
                return {'message': f'Invalid date format: {str(e)}'}, 400
            
            # Generate asset code
            asset_code = generate_asset_barcode(category.code, branch.id)
            
            # Check for duplicate barcode if provided
            if data.get('barcode'):
                existing = session.query(Asset).filter(Asset.barcode == data['barcode']).first()
                if existing:
                    return {'message': 'Barcode already exists'}, 409
            
            # Create new asset
            asset = Asset(
                asset_code=asset_code,
                name_en=data['name_en'],
                name_ar=data['name_ar'],
                description=data.get('description'),
                category_id=data['category_id'],
                branch_id=data['branch_id'],
                warehouse_id=data['warehouse_id'],
                purchase_date=purchase_date,
                purchase_value=data['purchase_value'],
                invoice_number=data.get('invoice_number'),
                supplier_name=data.get('supplier_name'),
                warranty_start_date=warranty_start_date,
                warranty_end_date=warranty_end_date,
                quantity=data.get('quantity', 1),
                unit=data.get('unit'),
                serial_number=data.get('serial_number'),
                model=data.get('model'),
                manufacturer=data.get('manufacturer'),
                location_notes=data.get('location_notes'),
                barcode=data.get('barcode'),
                rfid_tag=data.get('rfid_tag'),
                created_by=current_user_id
            )
            
            session.add(asset)
            session.commit()
            
            return {
                'message': 'Asset created successfully',
                'asset': asset.to_dict(include_relations=True)
            }, 201
            
        except Exception as e:
            session.rollback()
            return {'message': f'Failed to create asset: {str(e)}'}, 500
        finally:
            session.close()

@asset_ns.route('/<int:asset_id>')
class AssetDetail(Resource):
    @asset_ns.doc('get_asset')
    @jwt_required()
    @require_permission('view_assets')
    def get(self, asset_id):
        """Get a specific asset"""
        try:
            session = Session()
            asset = session.query(Asset).get(asset_id)
            
            if not asset:
                return {'message': 'Asset not found'}, 404
            
            return asset.to_dict(include_relations=True), 200
            
        except Exception as e:
            return {'message': f'Failed to retrieve asset: {str(e)}'}, 500
        finally:
            session.close()
    
    @asset_ns.expect(asset_model)
    @asset_ns.doc('update_asset')
    @jwt_required()
    @require_permission('manage_assets')
    def put(self, asset_id):
        """Update an asset"""
        try:
            data = request.get_json()
            
            session = Session()
            asset = session.query(Asset).get(asset_id)
            
            if not asset:
                return {'message': 'Asset not found'}, 404
            
            # Validate references if they are being updated
            if data.get('category_id'):
                category = session.query(AssetCategory).get(data['category_id'])
                if not category or not category.is_active:
                    return {'message': 'Invalid asset category'}, 400
                asset.category_id = data['category_id']
            
            if data.get('branch_id'):
                branch = session.query(Branch).get(data['branch_id'])
                if not branch or not branch.is_active:
                    return {'message': 'Invalid branch'}, 400
                asset.branch_id = data['branch_id']
            
            if data.get('warehouse_id'):
                warehouse = session.query(Warehouse).get(data['warehouse_id'])
                if not warehouse or not warehouse.is_active:
                    return {'message': 'Invalid warehouse'}, 400
                
                # Check if warehouse belongs to the selected branch
                branch_id = data.get('branch_id', asset.branch_id)
                if warehouse.branch_id != branch_id:
                    return {'message': 'Warehouse does not belong to selected branch'}, 400
                
                asset.warehouse_id = data['warehouse_id']
            
            # Update other fields
            updateable_fields = [
                'name_en', 'name_ar', 'description', 'purchase_value', 'invoice_number',
                'supplier_name', 'quantity', 'unit', 'serial_number', 'model', 
                'manufacturer', 'location_notes', 'current_value', 'status',
                'barcode', 'rfid_tag', 'last_maintenance_date', 'next_maintenance_date'
            ]
            
            for field in updateable_fields:
                if field in data:
                    setattr(asset, field, data[field])
            
            # Handle date fields
            date_fields = ['purchase_date', 'warranty_start_date', 'warranty_end_date']
            for field in date_fields:
                if field in data and data[field]:
                    try:
                        date_value = datetime.datetime.strptime(data[field], '%Y-%m-%d').date()
                        setattr(asset, field, date_value)
                    except ValueError:
                        return {'message': f'Invalid date format for {field}. Use YYYY-MM-DD'}, 400
            
            # Check for duplicate barcode if it's being updated
            if data.get('barcode') and data['barcode'] != asset.barcode:
                existing = session.query(Asset).filter(
                    Asset.barcode == data['barcode'],
                    Asset.id != asset_id
                ).first()
                if existing:
                    return {'message': 'Barcode already exists'}, 409
            
            asset.updated_at = datetime.datetime.utcnow()
            session.commit()
            
            return {
                'message': 'Asset updated successfully',
                'asset': asset.to_dict(include_relations=True)
            }, 200
            
        except Exception as e:
            session.rollback()
            return {'message': f'Failed to update asset: {str(e)}'}, 500
        finally:
            session.close()
    
    @asset_ns.doc('delete_asset')
    @jwt_required()
    @require_permission('delete_assets')
    def delete(self, asset_id):
        """Delete an asset"""
        try:
            session = Session()
            asset = session.query(Asset).get(asset_id)
            
            if not asset:
                return {'message': 'Asset not found'}, 404
            
            # Change status to DISPOSED instead of actually deleting
            asset.status = 'DISPOSED'
            asset.updated_at = datetime.datetime.utcnow()
            session.commit()
            
            return {'message': 'Asset marked as disposed successfully'}, 200
            
        except Exception as e:
            session.rollback()
            return {'message': f'Failed to delete asset: {str(e)}'}, 500
        finally:
            session.close()

@asset_ns.route('/statistics')
class AssetStatistics(Resource):
    @asset_ns.doc('get_asset_statistics')
    @jwt_required()
    @require_permission('view_assets')
    def get(self):
        """Get asset statistics"""
        try:
            session = Session()
            
            # Count assets by status
            from sqlalchemy import func
            status_counts = session.query(
                Asset.status, 
                func.count(Asset.id).label('count')
            ).group_by(Asset.status).all()
            
            # Count assets by category
            category_counts = session.query(
                AssetCategory.name_en.label('category_name'),
                func.count(Asset.id).label('count')
            ).join(AssetCategory, Asset.category_id == AssetCategory.id)\
             .group_by(AssetCategory.name_en).all()
            
            # Total value
            total_value = session.query(func.sum(Asset.purchase_value)).scalar() or 0
            current_value = session.query(func.sum(Asset.current_value)).scalar() or 0
            
            return {
                'total_assets': session.query(Asset).count(),
                'status_distribution': {status: count for status, count in status_counts},
                'category_distribution': {category: count for category, count in category_counts},
                'total_purchase_value': float(total_value),
                'total_current_value': float(current_value) if current_value else None,
                'depreciation': float(total_value - (current_value or 0))
            }, 200
            
        except Exception as e:
            return {'message': f'Failed to retrieve statistics: {str(e)}'}, 500
        finally:
            session.close()

@asset_ns.route('/search/<string:barcode>')
class AssetSearchByBarcode(Resource):
    @asset_ns.doc('search_asset_by_barcode')
    @jwt_required()
    @require_permission('view_assets')
    def get(self, barcode):
        """Search asset by barcode"""
        try:
            session = Session()
            asset = session.query(Asset).filter(Asset.barcode == barcode).first()
            
            if not asset:
                return {'message': 'Asset not found'}, 404
            
            return asset.to_dict(include_relations=True), 200
            
        except Exception as e:
            return {'message': f'Failed to search asset: {str(e)}'}, 500
        finally:
            session.close()
