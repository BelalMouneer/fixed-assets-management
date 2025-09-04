#!/usr/bin/env python3
"""
Quick Start Script for Fixed Assets Management System
This script helps you start the application quickly by setting up a local SQLite database for testing
"""

import os
import sys
from datetime import datetime, date

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_sqlite_config():
    """Create a SQLite configuration for quick testing"""
    config_content = '''# SQLite Configuration for Quick Testing
DATABASE_URL = "sqlite:///./fixed_assets_test.db"
DATABASE_DRIVER_NAME = "sqlite"
DATABASE_USERNAME = ""
DATABASE_PASSWORD = ""  
DATABASE_HOST = ""
DATABASE_NAME = "fixed_assets_test.db"
DATABASE_PORT = ""

SECRET_KEY = "your-secret-key-for-development-change-in-production"
JWT_SECRET_KEY = "your-jwt-secret-key-change-in-production"

# JWT Configuration
JWT_ACCESS_TOKEN_EXPIRES = 86400
JWT_REFRESH_TOKEN_EXPIRES = 2592000

# CORS Configuration
ENABLE_CORS = True

# File Upload Configuration  
UPLOAD_FOLDER = "./uploads"
MAX_CONTENT_LENGTH = 16777216

# App Configuration
DEBUG = True
TESTING = False

# Database Connection Pool
DATABASE_POOL_SIZE = 5
DATABASE_POOL_RECYCLE = 3600
'''
    
    # Create config directory if it doesn't exist
    os.makedirs('config', exist_ok=True)
    
    with open('config/app_local.cfg', 'w') as f:
        f.write(config_content)
    
    print("✓ Created SQLite configuration file: config/app_local.cfg")

def quick_setup():
    """Quick setup for testing with SQLite"""
    print("🚀 Fixed Assets Management System - Quick Setup")
    print("=" * 50)
    
    try:
        # Create SQLite config
        create_sqlite_config()
        
        # Import and create basic setup
        from modules.app import app
        from modules.models.models import Base, db_engine
        
        print("📦 Creating database tables...")
        with app.app_context():
            Base.metadata.create_all(db_engine)
        print("✓ Database tables created successfully")
        
        # Basic data setup
        from modules.app import Session
        from modules.models.models import (
            Company, Branch, Position, Permission, User, 
            AssetCategory, SystemSettings
        )
        
        session = Session()
        
        try:
            # Create basic company (ID=1)
            if not session.query(Company).filter_by(id=1).first():
                company = Company(
                    id=1,
                    name_en='Test Company',
                    name_ar='الشركة التجريبية', 
                    address_en='Test Address',
                    address_ar='العنوان التجريبي',
                    phone='+1234567890',
                    email='test@company.com'
                )
                session.add(company)
                session.flush()
                print("✓ Created test company")
            
            # Create main branch
            if not session.query(Branch).first():
                branch = Branch(
                    name_en='Main Branch',
                    name_ar='الفرع الرئيسي',
                    address_en='Main Address',
                    address_ar='العنوان الرئيسي',
                    phone='+1234567891',
                    email='main@company.com'
                )
                session.add(branch)
                session.flush()
                print("✓ Created main branch")
            
            # Create admin position
            if not session.query(Position).filter_by(name_en='System Administrator').first():
                admin_position = Position(
                    name_en='System Administrator',
                    name_ar='مدير النظام',
                    description='Full system access',
                    level=10
                )
                session.add(admin_position)
                session.flush()
                print("✓ Created admin position")
            
            # Create admin user
            if not session.query(User).filter_by(username='admin').first():
                admin_user = User(
                    username='admin',
                    email='admin@company.com',
                    first_name='System',
                    last_name='Admin',
                    position_id=admin_position.id,
                    branch_id=branch.id,
                    employee_id='ADMIN001',
                    status='ACTIVE'
                )
                admin_user.set_password('Admin@123456')
                session.add(admin_user)
                session.flush()
                print("✓ Created admin user (admin / Admin@123456)")
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error creating basic data: {e}")
        finally:
            session.close()
        
        print("\n🎉 Quick setup completed successfully!")
        print("\n📋 Quick Start Information:")
        print(f"• Database: SQLite (fixed_assets_test.db)")
        print(f"• Admin Username: admin")
        print(f"• Admin Password: Admin@123456")
        print(f"• API will run on: http://localhost:5000")
        print(f"• API Documentation: http://localhost:5000/docs")
        
        print(f"\n🚀 To start the application run:")
        print(f"   python main.py")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def start_app():
    """Start the Flask application"""
    from main import app
    print("🌟 Starting Fixed Assets Management System...")
    print("📡 API Documentation available at: http://localhost:5000/docs")
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'start':
        start_app()
    else:
        if quick_setup():
            print("\n" + "=" * 50)
            response = input("🚀 Would you like to start the application now? (y/n): ")
            if response.lower() in ['y', 'yes']:
                start_app()
