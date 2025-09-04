"""
API Blueprint Registration Module
"""

from modules.app import app, api

def register_apis():
    """Register all API blueprints with the Flask application"""
    
    # Import all API modules
    from modules.api.auth import auth_ns
    from modules.api.company import company_ns
    from modules.api.branch import branch_ns
    from modules.api.warehouse import warehouse_ns
    from modules.api.position import position_ns
    from modules.api.permission import permission_ns
    from modules.api.user import user_ns
    from modules.api.asset_category import asset_category_ns
    from modules.api.asset import asset_ns
    from modules.api.asset_transfer import asset_transfer_ns
    from modules.api.asset_maintenance import asset_maintenance_ns
    from modules.api.reports import reports_ns
    from modules.api.barcode import barcode_ns
    from modules.api.upload import upload_ns
    
    # Register namespaces with Flask-RESTX
    api.add_namespace(auth_ns, path='/api/auth')
    api.add_namespace(company_ns, path='/api/companies')
    api.add_namespace(branch_ns, path='/api/branches')
    api.add_namespace(warehouse_ns, path='/api/warehouses')
    api.add_namespace(position_ns, path='/api/positions')
    api.add_namespace(permission_ns, path='/api/permissions')
    api.add_namespace(user_ns, path='/api/users')
    api.add_namespace(asset_category_ns, path='/api/asset-categories')
    api.add_namespace(asset_ns, path='/api/assets')
    api.add_namespace(asset_transfer_ns, path='/api/asset-transfers')
    api.add_namespace(asset_maintenance_ns, path='/api/asset-maintenance')
    api.add_namespace(reports_ns, path='/api/reports')
    api.add_namespace(barcode_ns, path='/api/barcode')
    api.add_namespace(upload_ns, path='/api/upload')
    
    print("✓ All API endpoints registered successfully")
