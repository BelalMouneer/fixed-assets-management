#!/usr/bin/env python3
"""
Database Initialization Script for Fixed Assets Management System
Creates tables and populates initial data including permissions, positions, and admin user
"""

import sys
import os
from datetime import datetime, date

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.app import db_engine, Session
from modules.models.models import (
    Base, Company, Branch, Warehouse, Position, Permission, User, 
    AssetCategory, SystemSettings, position_permissions
)

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(db_engine)
    print("✓ Database tables created successfully")

def create_permissions():
    """Create initial permissions"""
    print("Creating permissions...")
    
    permissions_data = [
        # Company management
        ('manage_company', 'Manage Company', 'Full access to company information management', 'company'),
        ('view_company', 'View Company', 'View company information', 'company'),
        
        # Branch management  
        ('manage_branches', 'Manage Branches', 'Full access to branch management', 'branch'),
        ('view_branches', 'View Branches', 'View branch information', 'branch'),
        
        # Warehouse management
        ('manage_warehouses', 'Manage Warehouses', 'Full access to warehouse management', 'warehouse'),
        ('view_warehouses', 'View Warehouses', 'View warehouse information', 'warehouse'),
        
        # User management
        ('manage_users', 'Manage Users', 'Full access to user management', 'user'),
        ('view_users', 'View Users', 'View user information', 'user'),
        ('reset_user_passwords', 'Reset User Passwords', 'Reset other users passwords', 'user'),
        
        # Position management
        ('manage_positions', 'Manage Positions', 'Full access to position/role management', 'position'),
        ('view_positions', 'View Positions', 'View position/role information', 'position'),
        
        # Permission management
        ('manage_permissions', 'Manage Permissions', 'Full access to permission management', 'permission'),
        ('view_permissions', 'View Permissions', 'View permission information', 'permission'),
        
        # Asset management
        ('manage_assets', 'Manage Assets', 'Full access to asset management', 'asset'),
        ('view_assets', 'View Assets', 'View asset information', 'asset'),
        ('delete_assets', 'Delete Assets', 'Delete/dispose assets', 'asset'),
        ('transfer_assets', 'Transfer Assets', 'Transfer assets between locations', 'asset'),
        
        # Asset categories
        ('manage_asset_categories', 'Manage Asset Categories', 'Full access to asset category management', 'asset'),
        ('view_asset_categories', 'View Asset Categories', 'View asset category information', 'asset'),
        
        # Asset maintenance
        ('manage_maintenance', 'Manage Asset Maintenance', 'Full access to asset maintenance management', 'maintenance'),
        ('view_maintenance', 'View Asset Maintenance', 'View asset maintenance records', 'maintenance'),
        
        # Reports
        ('generate_reports', 'Generate Reports', 'Generate and view reports', 'report'),
        ('view_financial_reports', 'View Financial Reports', 'View financial reports and analytics', 'report'),
        ('export_data', 'Export Data', 'Export data to various formats', 'report'),
        
        # Barcode system
        ('generate_barcodes', 'Generate Barcodes', 'Generate and print barcodes', 'barcode'),
        ('scan_barcodes', 'Scan Barcodes', 'Scan and lookup barcodes', 'barcode'),
        
        # File management
        ('upload_files', 'Upload Files', 'Upload files and attachments', 'file'),
        ('delete_files', 'Delete Files', 'Delete files and attachments', 'file'),
        
        # System administration
        ('system_admin', 'System Administration', 'Full system administration access', 'system'),
        ('view_audit_logs', 'View Audit Logs', 'View system audit logs', 'system'),
        ('manage_system_settings', 'Manage System Settings', 'Manage system configuration', 'system'),
    ]
    
    session = Session()
    
    try:
        for code, name, description, module in permissions_data:
            # Check if permission already exists
            existing = session.query(Permission).filter(Permission.code == code).first()
            if not existing:
                permission = Permission(
                    code=code,
                    name=name,
                    description=description,
                    module=module
                )
                session.add(permission)
        
        session.commit()
        print(f"✓ Created {len(permissions_data)} permissions")
        
    except Exception as e:
        session.rollback()
        print(f"Error creating permissions: {e}")
        raise
    finally:
        session.close()

def create_positions():
    """Create initial positions/roles"""
    print("Creating positions...")
    
    positions_data = [
        ('System Administrator', 'مدير النظام', 'Full system access with all permissions', 10),
        ('General Manager', 'المدير العام', 'General management access', 9),
        ('IT Manager', 'مدير تقنية المعلومات', 'IT management and system administration', 8),
        ('Assets Manager', 'مدير الأصول الثابتة', 'Fixed assets management', 7),
        ('Branch Manager', 'مدير الفرع', 'Branch-level management access', 6),
        ('Warehouse Manager', 'مدير المستودع', 'Warehouse operations management', 5),
        ('Assets Supervisor', 'مشرف الأصول', 'Assets supervision and monitoring', 4),
        ('Data Entry Clerk', 'موظف إدخال البيانات', 'Basic data entry access', 3),
        ('Maintenance Technician', 'فني الصيانة', 'Asset maintenance operations', 3),
        ('Accountant', 'المحاسب', 'Financial reporting and asset valuation', 4),
        ('Auditor', 'المدقق', 'Read-only access for auditing', 2),
        ('User', 'مستخدم', 'Basic user access', 1),
    ]
    
    session = Session()
    
    try:
        created_positions = {}
        
        for name_en, name_ar, description, level in positions_data:
            # Check if position already exists
            existing = session.query(Position).filter(Position.name_en == name_en).first()
            if not existing:
                position = Position(
                    name_en=name_en,
                    name_ar=name_ar,
                    description=description,
                    level=level
                )
                session.add(position)
                session.flush()  # Get the ID
                created_positions[name_en] = position
        
        session.commit()
        print(f"✓ Created positions")
        
        # Assign permissions to positions
        assign_permissions_to_positions(session, created_positions)
        
    except Exception as e:
        session.rollback()
        print(f"Error creating positions: {e}")
        raise
    finally:
        session.close()

def assign_permissions_to_positions(session, created_positions):
    """Assign permissions to positions"""
    print("Assigning permissions to positions...")
    
    # Get all permissions
    all_permissions = {p.code: p for p in session.query(Permission).all()}
    all_positions = {p.name_en: p for p in session.query(Position).all()}
    
    # Define permission assignments
    permission_assignments = {
        'System Administrator': list(all_permissions.keys()),  # All permissions
        
        'General Manager': [
            'view_company', 'manage_company', 'view_branches', 'manage_branches',
            'view_warehouses', 'manage_warehouses', 'view_users', 'manage_users',
            'view_assets', 'manage_assets', 'transfer_assets', 'view_asset_categories',
            'generate_reports', 'view_financial_reports', 'export_data'
        ],
        
        'IT Manager': [
            'view_company', 'view_branches', 'view_warehouses', 'manage_users',
            'view_users', 'manage_permissions', 'view_permissions', 'system_admin',
            'view_audit_logs', 'manage_system_settings', 'generate_barcodes'
        ],
        
        'Assets Manager': [
            'view_company', 'view_branches', 'view_warehouses', 'view_users',
            'manage_assets', 'view_assets', 'delete_assets', 'transfer_assets',
            'manage_asset_categories', 'view_asset_categories', 'manage_maintenance',
            'view_maintenance', 'generate_reports', 'export_data', 'generate_barcodes',
            'scan_barcodes', 'upload_files'
        ],
        
        'Branch Manager': [
            'view_company', 'view_branches', 'view_warehouses', 'view_users',
            'view_assets', 'manage_assets', 'transfer_assets', 'view_asset_categories',
            'view_maintenance', 'generate_reports', 'scan_barcodes'
        ],
        
        'Warehouse Manager': [
            'view_warehouses', 'view_assets', 'manage_assets', 'transfer_assets',
            'view_asset_categories', 'view_maintenance', 'scan_barcodes', 'upload_files'
        ],
        
        'Assets Supervisor': [
            'view_assets', 'manage_assets', 'view_asset_categories', 'view_maintenance',
            'manage_maintenance', 'scan_barcodes', 'upload_files'
        ],
        
        'Data Entry Clerk': [
            'view_assets', 'manage_assets', 'view_asset_categories', 'upload_files'
        ],
        
        'Maintenance Technician': [
            'view_assets', 'view_maintenance', 'manage_maintenance', 'scan_barcodes'
        ],
        
        'Accountant': [
            'view_company', 'view_assets', 'view_asset_categories', 'generate_reports',
            'view_financial_reports', 'export_data'
        ],
        
        'Auditor': [
            'view_company', 'view_branches', 'view_warehouses', 'view_users',
            'view_assets', 'view_asset_categories', 'view_maintenance',
            'generate_reports', 'view_financial_reports', 'view_audit_logs'
        ],
        
        'User': [
            'view_assets', 'view_asset_categories', 'scan_barcodes'
        ]
    }
    
    try:
        for position_name, permission_codes in permission_assignments.items():
            position = all_positions.get(position_name)
            if position:
                for perm_code in permission_codes:
                    permission = all_permissions.get(perm_code)
                    if permission and permission not in position.permissions:
                        position.permissions.append(permission)
        
        session.commit()
        print("✓ Assigned permissions to positions")
        
    except Exception as e:
        session.rollback()
        print(f"Error assigning permissions: {e}")
        raise

def create_sample_data():
    """Create single company, branch, warehouse, and admin user"""
    print("Creating sample data...")
    
    session = Session()
    
    try:
        # Create the single company (static with ID=1)
        company = Company(
            id=1,
            name_en='Fixed Assets Management Company',
            name_ar='شركة إدارة الأصول الثابتة',
            address_en='123 Business Street, Business District, City',
            address_ar='123 شارع الأعمال، منطقة الأعمال، المدينة',
            phone='+1234567890',
            email='info@fixedassets.com',
            commercial_registry='CR123456789',
            tax_number='TAX987654321',
            website='https://www.fixedassets.com'
        )
        session.add(company)
        session.flush()
        print("✓ Created single company with ID=1")
        
        # Create main branch (defaults to company_id=1)
        branch = Branch(
            name_en='Main Branch',
            name_ar='الفرع الرئيسي',
            address_en='Main Branch Address',
            address_ar='عنوان الفرع الرئيسي',
            phone='+1234567891',
            email='main@fixedassets.com',
            manager_name='Branch Manager'
        )
        session.add(branch)
        session.flush()
        
        # Create sample warehouse
        warehouse = Warehouse(
            branch_id=branch.id,
            name_en='Main Warehouse',
            name_ar='المستودع الرئيسي',
            location='Ground Floor, Main Building',
            description='Primary storage facility',
            capacity=1000.0,
            manager_name='Warehouse Manager'
        )
        session.add(warehouse)
        session.flush()
        
        # Create sample asset categories
        categories_data = [
            ('COMP', 'Computer Equipment', 'معدات الحاسوب', 'Desktop computers, laptops, servers', 25.0, 4),
            ('FURN', 'Furniture', 'الأثاث', 'Office furniture and fixtures', 10.0, 10),
            ('VEHI', 'Vehicles', 'المركبات', 'Company vehicles and transportation', 20.0, 5),
            ('MACH', 'Machinery', 'الآلات', 'Industrial machinery and equipment', 15.0, 8),
            ('ELEC', 'Electronics', 'الإلكترونيات', 'Electronic equipment and devices', 30.0, 3),
        ]
        
        for code, name_en, name_ar, desc, dep_rate, useful_life in categories_data:
            category = AssetCategory(
                code=code,
                name_en=name_en,
                name_ar=name_ar,
                description=desc,
                depreciation_rate=dep_rate,
                useful_life_years=useful_life
            )
            session.add(category)
        
        session.flush()
        
        # Create admin user
        admin_position = session.query(Position).filter(Position.name_en == 'System Administrator').first()
        
        admin_user = User(
            username='admin',
            email='admin@samplecompany.com',
            first_name='System',
            last_name='Administrator',
            phone='+1234567892',
            position_id=admin_position.id,
            branch_id=branch.id,
            employee_id='EMP001',
            hire_date=date.today()
        )
        admin_user.set_password('Admin@123456')  # Strong default password
        session.add(admin_user)
        
        # Create system settings
        settings_data = [
            ('company_logo_url', '', 'URL for company logo', 'string'),
            ('default_currency', 'USD', 'Default currency for the system', 'string'),
            ('asset_code_format', '{category}-BR{branch:03d}-{year}-{seq:04d}', 'Asset code generation format', 'string'),
            ('barcode_format', 'CODE128', 'Default barcode format', 'string'),
            ('maintenance_reminder_days', '30', 'Days before maintenance reminder', 'integer'),
            ('backup_retention_days', '90', 'Number of days to keep backups', 'integer'),
            ('max_file_upload_size', '16777216', 'Maximum file upload size in bytes (16MB)', 'integer'),
            ('allowed_file_types', 'pdf,doc,docx,xls,xlsx,jpg,jpeg,png,gif,txt', 'Allowed file upload types', 'string'),
        ]
        
        for key, value, description, data_type in settings_data:
            setting = SystemSettings(
                key=key,
                value=value,
                description=description,
                data_type=data_type,
                updated_by=admin_user.id
            )
            session.add(setting)
        
        session.commit()
        
        print("✓ Created sample data:")
        print(f"  - Company: {company.name_en}")
        print(f"  - Branch: {branch.name_en}")
        print(f"  - Warehouse: {warehouse.name_en}")
        print(f"  - Asset Categories: {len(categories_data)} categories")
        print(f"  - Admin User: {admin_user.username} (password: Admin@123456)")
        print("  - System Settings: Basic configuration")
        
    except Exception as e:
        session.rollback()
        print(f"Error creating sample data: {e}")
        raise
    finally:
        session.close()

def main():
    """Main initialization function"""
    print("Fixed Assets Management System - Database Initialization")
    print("=" * 60)
    
    try:
        # Create tables
        create_tables()
        
        # Create initial data
        create_permissions()
        create_positions()
        create_sample_data()
        
        print("\n" + "=" * 60)
        print("✓ Database initialization completed successfully!")
        print("\nYou can now start the application with:")
        print("python main.py")
        print("\nDefault admin credentials:")
        print("Username: admin")
        print("Password: Admin@123456")
        print("\nAPI Documentation: http://localhost:5000/docs/")
        
    except Exception as e:
        print(f"\n❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()