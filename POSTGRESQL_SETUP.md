# PostgreSQL Setup Guide for Fixed Assets Management System

This guide will help you set up PostgreSQL for the Fixed Assets Management System.

## 📋 Prerequisites

1. **PostgreSQL 15+ installed** on your system
2. **pgAdmin** (optional but recommended for database management)
3. **Python environment** with all requirements installed

## 🚀 Step 1: Install PostgreSQL

### Windows:
1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Run the installer and follow the setup wizard
3. Remember the password you set for the `postgres` user
4. Default port is usually `5432`

### Alternative - Using Docker:
```bash
# Run PostgreSQL in Docker
docker run -d \
  --name postgres-fixed-assets \
  -e POSTGRES_DB=fixed_assets_management_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  postgres:15
```

## 🗄️ Step 2: Create Database

### Option A: Using psql command line:
```bash
# Connect to PostgreSQL
psql -U postgres -h localhost

# Create the database
CREATE DATABASE fixed_assets_management_db;

# Create a dedicated user (optional but recommended)
CREATE USER fixed_assets_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE fixed_assets_management_db TO fixed_assets_user;

# Exit psql
\q
```

### Option B: Using pgAdmin:
1. Open pgAdmin
2. Connect to your PostgreSQL server
3. Right-click "Databases" → "Create" → "Database"
4. Name: `fixed_assets_management_db`
5. Click "Save"

## ⚙️ Step 3: Update Configuration

Update your `config/app_local.cfg` file with your PostgreSQL details:

```python
# PostgreSQL Configuration
DATABASE_DRIVER_NAME = "postgresql+psycopg2"
DATABASE_USERNAME = "postgres"  # or your custom user
DATABASE_PASSWORD = "your_password"  # your actual password
DATABASE_HOST = "localhost"
DATABASE_NAME = "fixed_assets_management_db" 
DATABASE_PORT = 5432
```

## 🏗️ Step 4: Initialize Database

Run the database initialization script:

```bash
# Activate your virtual environment
.\venv\Scripts\activate

# Initialize the database with tables and sample data
python init_db.py
```

This will create:
- ✅ All database tables
- ✅ 25+ permission types
- ✅ 12 predefined user positions/roles
- ✅ Sample company and branch
- ✅ Asset categories
- ✅ Admin user (username: `admin`, password: `Admin@123456`)

## 🚀 Step 5: Start the Application

```bash
# Start the Flask application
python main.py
```

The API will be available at:
- **API Base**: http://localhost:5000
- **API Documentation**: http://localhost:5000/docs
- **Health Check**: http://localhost:5000/

## 🔐 Step 6: Test Login

Use these credentials to test:
- **Username**: `admin`
- **Password**: `Admin@123456`

### Test with curl:
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Admin@123456"}'
```

## 📊 Database Schema Overview

Your PostgreSQL database will have these main tables:

### Core Tables:
- `company` - Single company information
- `branches` - Multiple branches within the company
- `warehouses` - Storage locations within branches
- `positions` - Job positions/roles
- `permissions` - Granular permission system
- `users` - System users with position-based access

### Asset Management:
- `asset_categories` - Asset classification
- `assets` - Fixed assets with complete tracking
- `asset_attachments` - Files and documents
- `asset_transfers` - Asset movement history
- `asset_maintenance` - Maintenance scheduling

### Audit & Settings:
- `audit_logs` - Complete audit trail
- `system_settings` - Configurable system parameters

## 🔧 Troubleshooting

### Common Issues:

1. **Connection refused**:
   - Check if PostgreSQL service is running
   - Verify port 5432 is not blocked
   - Check username/password

2. **Database doesn't exist**:
   - Run Step 2 to create the database first
   - Check database name spelling

3. **Permission denied**:
   - Verify user has proper database privileges
   - Check pg_hba.conf for authentication method

4. **Module not found errors**:
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

## 🐳 Docker Alternative (Complete Setup)

If you prefer Docker, use the provided docker-compose.yml:

```bash
# Start all services (PostgreSQL + API + pgAdmin)
docker-compose up -d

# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f api
```

This will start:
- PostgreSQL on port 5432
- API on port 5000  
- pgAdmin on port 8080

## 🎯 Why PostgreSQL?

✅ **Production Ready**: Handles concurrent users and large datasets
✅ **ACID Compliance**: Ensures data integrity for financial assets
✅ **Advanced Features**: JSON support, full-text search, spatial data
✅ **Scalability**: Can handle millions of assets and transactions  
✅ **Backup & Recovery**: Enterprise-level data protection
✅ **Performance**: Optimized for complex queries and reporting
✅ **Security**: Row-level security, encryption, audit logging

SQLite is great for development/testing, but PostgreSQL is essential for:
- Multiple concurrent users
- Large asset databases
- Financial reporting accuracy
- Production deployment
- Data backup and recovery

## 📞 Need Help?

If you encounter any issues:
1. Check the application logs
2. Verify PostgreSQL is running: `pg_isready -h localhost -p 5432`
3. Test database connection: `psql -U postgres -h localhost -d fixed_assets_management_db`
4. Check the Flask application logs for detailed error messages
