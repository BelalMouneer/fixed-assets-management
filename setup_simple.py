#!/usr/bin/env python3
"""
Simple PostgreSQL Setup for Fixed Assets Management System
"""

import os
import sys

def main():
    """Main setup process"""
    print("🐘 Fixed Assets Management System - PostgreSQL Setup")
    print("=" * 60)
    
    print("📋 Make sure PostgreSQL is running with these settings:")
    print("  • Host: localhost")
    print("  • Port: 5432")
    print("  • Database: fixed_assets_management_db")
    print("  • Username: belal")  
    print("  • Password: belal")
    print()
    
    # Check if we can import the modules
    try:
        print("🔍 Testing database connection...")
        
        # Add current directory to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Test if we can load the app
        from modules.app import app, db_engine
        print("✅ Application modules loaded successfully")
        
        # Test database connection
        with db_engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ Database connection successful")
        
        print("\n🏗️ Initializing database...")
        # Run database initialization
        result = os.system(f"{sys.executable} init_db.py")
        
        if result == 0:
            print("\n🎉 Setup completed successfully!")
            print("\n📋 System Information:")
            print(f"• Database: PostgreSQL")
            print(f"• Database Name: fixed_assets_management_db") 
            print(f"• Admin Username: admin")
            print(f"• Admin Password: Admin@123456")
            print(f"• API URL: http://localhost:5000")
            print(f"• API Docs: http://localhost:5000/docs")
            
            print(f"\n🚀 To start the application:")
            print(f"   python main.py")
            
            print(f"\n🔐 Test login:")
            print(f'   curl -X POST http://localhost:5000/auth/login \\')
            print(f'     -H "Content-Type: application/json" \\')
            print(f'     -d \'{{"username": "admin", "password": "Admin@123456"}}\'')
            
            return True
        else:
            print("❌ Database initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("\n💡 Please ensure:")
        print("  1. PostgreSQL is installed and running")
        print("  2. Database 'fixed_assets_management_db' exists (or PostgreSQL user can create it)")
        print("  3. Username 'belal' and password 'belal' are correct")
        print("  4. Port 5432 is accessible")
        print(f"\n📖 For detailed setup instructions, see POSTGRESQL_SETUP.md")
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)
