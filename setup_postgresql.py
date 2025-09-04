#!/usr/bin/env python3
"""
PostgreSQL Setup Script for Fixed Assets Management System
This script helps you set up the PostgreSQL database and initialize the system
"""

import os
import sys
import subprocess
from datetime import datetime
import configparser

def check_postgresql():
    """Check if PostgreSQL is running and accessible"""
    print("🔍 Checking PostgreSQL connection...")
    
    try:
        import psycopg2
        # Read config from app_local.cfg
        config = configparser.ConfigParser()
        config.read('config/app_local.cfg')
        DATABASE_HOST = config.get('database', 'host')
        DATABASE_PORT = config.get('database', 'port')
        DATABASE_USERNAME = config.get('database', 'username')
        DATABASE_PASSWORD = config.get('database', 'password')
        DATABASE_NAME = config.get('database', 'name')
        
        # Try to connect to PostgreSQL server (not the specific database yet)
        conn = psycopg2.connect(
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            user=DATABASE_USERNAME,
            password=DATABASE_PASSWORD,
            database='postgres'  # Connect to default postgres database first
        )
        conn.close()
        print("✅ PostgreSQL server is running and accessible")
        return True
        
    except ImportError:
        print("❌ psycopg2 not installed. Run: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Cannot connect to PostgreSQL: {e}")
        print("\n📋 Please check:")
        print("  • PostgreSQL is installed and running")
        print("  • Username and password are correct in config/app_local.cfg")
        print("  • Port 5432 is accessible")
        return False

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Read config from app_local.cfg
        # Read config from app_local.cfg
        config = configparser.ConfigParser()
        config.read('config/app_local.cfg')
        DATABASE_HOST = config.get('database', 'host')
        DATABASE_PORT = config.get('database', 'port')
        DATABASE_USERNAME = config.get('database', 'username')
        DATABASE_PASSWORD = config.get('database', 'password')
        DATABASE_NAME = config.get('database', 'name')
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host=DATABASE_HOST,
            port=DATABASE_PORT, 
            user=DATABASE_USERNAME,
            password=DATABASE_PASSWORD,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DATABASE_NAME,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {DATABASE_NAME}")
            print(f"✅ Created database: {DATABASE_NAME}")
        else:
            print(f"✅ Database {DATABASE_NAME} already exists")
            
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False

def initialize_database():
    """Initialize database tables and data"""
    print("🏗️ Initializing database tables and data...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Run the init_db script
        from init_db import main as init_main
        
        success = init_main()
        if success:
            print("✅ Database initialized successfully!")
            return True
        else:
            print("❌ Database initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_application():
    """Test if the application can start"""
    print("🧪 Testing application startup...")
    
    try:
        from main import app
        print("✅ Application loads successfully!")
        return True
    except Exception as e:
        print(f"❌ Application failed to load: {e}")
        return False

def main():
    """Main setup process"""
    print("🐘 Fixed Assets Management System - PostgreSQL Setup")
    print("=" * 60)
    
    # Step 1: Check PostgreSQL
    if not check_postgresql():
        print("\n❌ Setup aborted. Please install and configure PostgreSQL first.")
        print("📖 See POSTGRESQL_SETUP.md for detailed instructions.")
        return False
    
    # Step 2: Create database
    if not create_database():
        return False
    
    # Step 3: Initialize database
    if not initialize_database():
        return False
    
    # Step 4: Test application
    if not test_application():
        return False
    
    print("\n" + "=" * 60)
    print("🎉 PostgreSQL setup completed successfully!")
    print("\n📋 System Information:")
    print(f"• Database: PostgreSQL")
    print(f"• Database Name: fixed_assets_management_db")
    print(f"• Admin Username: admin")
    print(f"• Admin Password: Admin@123456")
    print(f"• API URL: http://localhost:5000")
    print(f"• API Docs: http://localhost:5000/docs")
    
    print(f"\n🚀 To start the application:")
    print(f"   python main.py")
    
    print(f"\n🔐 Test login with curl:")
    print(f'   curl -X POST http://localhost:5000/auth/login \\')
    print(f'     -H "Content-Type: application/json" \\')
    print(f'     -d \'{{"username": "admin", "password": "Admin@123456"}}\'')
    
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)
