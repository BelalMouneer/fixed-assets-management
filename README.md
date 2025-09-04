# Fixed Assets Management System

A comprehensive Fixed Assets Management System built with Python Flask, PostgreSQL, and modern web technologies. This system provides complete asset tracking, management, and reporting capabilities with role-based access control.

## 🚀 Features

### Core Functionality
- **Single Company Architecture**: Simplified single-company system with Arabic/English support
- **Branch Management**: Multiple branches within the company with full location tracking
- **Warehouse Management**: Warehouses linked to branches with capacity management
- **Job Positions**: Comprehensive position/role management system with automatic permission inheritance
- **Fixed Assets**: Complete asset lifecycle management with barcode/QR code support
- **User Management**: Admin-controlled user creation with role-based permissions (no signup)
- **File Attachments**: Upload and manage asset-related documents and images

### Asset Management Features
- Asset categorization with depreciation calculations
- Purchase information tracking (date, value, supplier, warranty)
- Physical tracking (serial numbers, models, manufacturers)
- Location management (branch, warehouse, notes)
- Status tracking (Active, Inactive, Maintenance, Disposed)
- Barcode and QR code generation and scanning
- Asset transfer management between locations
- Maintenance scheduling and tracking

### Reporting & Analytics
- Comprehensive asset reports with filtering
- Financial reports and depreciation tracking
- Asset utilization analytics
- Export capabilities (PDF, Excel, CSV)
- Dashboard with key metrics and charts

### Security & Permissions
- JWT-based authentication (login only - no public registration)
- 31+ granular permissions system inherited from positions
- Admin-controlled user creation and management
- Automatic permission inheritance based on user position/role
- Audit logging for all operations
- Password strength requirements

## 🛠️ Technology Stack

- **Backend**: Python Flask 2.3.2
- **API**: Flask-RESTX (Swagger/OpenAPI documentation)
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+
- **Authentication**: JWT (Flask-JWT-Extended)
- **Database Migrations**: Alembic
- **Barcode Generation**: python-barcode, qrcode
- **File Processing**: Pillow (PIL)
- **Reports**: ReportLab (PDF), openpyxl (Excel)

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Git (for version control)

## 🚀 Quick Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd fixed_assets_back
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL Database
```bash
# Create database 'fixed_assets_management_db'
# Update config/app_local.cfg with your database credentials
```

### 5. Initialize Database
```bash
python init_db.py
```

### 6. Start the Application
```bash
python main.py
```

## 🔐 Default Credentials

- **Username**: `admin`
- **Password**: `Admin@123456`

## 📡 API Endpoints

- **Base URL**: http://localhost:5000
- **API Documentation**: http://localhost:5000/docs
- **Health Check**: http://localhost:5000/api/health

### Authentication Endpoints
```
POST /auth/login              - User login
POST /auth/refresh            - Refresh access token  
GET  /auth/me                 - Get current user info
POST /auth/change-password    - Change password
POST /auth/create-user        - Create new user (admin only)
POST /auth/logout             - Logout user
```

## 🏗️ Database Schema

### Core Tables
- `company` - Single company information (ID=1)
- `branches` - Multiple branches within the company
- `warehouses` - Storage locations within branches
- `positions` - Job positions/roles with permissions
- `users` - System users with position-based access

### Asset Management
- `asset_categories` - Asset classification
- `assets` - Fixed assets with complete tracking
- `asset_attachments` - Files and documents
- `asset_transfers` - Asset movement history
- `asset_maintenance` - Maintenance scheduling

## 🎯 System Architecture

### Permission System
- **31 Granular Permissions**: Complete access control
- **12 Predefined Positions**: From System Admin to Basic User
- **Automatic Inheritance**: Users get permissions from their position
- **No Direct User Permissions**: Simplified management

### Position Hierarchy
1. **System Administrator** - Full access (all 31 permissions)
2. **General Manager** - Management access
3. **IT Manager** - IT and system administration
4. **Assets Manager** - Fixed assets management
5. **Branch Manager** - Branch-level operations
6. **Warehouse Manager** - Warehouse operations
7. **Assets Supervisor** - Asset supervision
8. **Data Entry Clerk** - Basic data entry
9. **Maintenance Technician** - Asset maintenance
10. **Accountant** - Financial reports
11. **Auditor** - Read-only access
12. **User** - Basic user access

## 🐳 Docker Deployment

```bash
# Start all services (PostgreSQL + API + pgAdmin)
docker-compose up -d

# View logs
docker-compose logs -f api
```

Services:
- PostgreSQL on port 5432
- API on port 5000
- pgAdmin on port 8080

## 📊 Configuration

### Database Configuration (config/app_local.cfg)
```python
DATABASE_DRIVER_NAME = "postgresql+psycopg2"
DATABASE_USERNAME = "your_username"
DATABASE_PASSWORD = "your_password"
DATABASE_HOST = "localhost"
DATABASE_NAME = "fixed_assets_management_db"
DATABASE_PORT = 5432
```

### JWT Configuration
```python
JWT_SECRET_KEY = "your-jwt-secret-key"
JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days
```

## 🧪 Testing

```bash
# Test database connection
python -c "from modules.app import db_engine; print('DB Connected!')"

# Test login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Admin@123456"}'
```

## 📝 Usage Examples

### Create a New User (Admin Required)
```bash
curl -X POST http://localhost:5000/auth/create-user \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "username": "manager1",
    "email": "manager@company.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Manager", 
    "position_id": 2,
    "branch_id": 1
  }'
```

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check PostgreSQL is running
   - Verify credentials in config/app_local.cfg
   - Ensure database exists

2. **Permission Denied**
   - Check user position has required permissions
   - Verify JWT token is valid

3. **Import Errors**
   - Ensure virtual environment is activated
   - Install missing dependencies with pip

## 📚 Documentation

- **API Documentation**: Available at `/docs` when running
- **Database Schema**: See `modules/models/models.py`
- **Permission System**: See `modules/utils/permissions.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the troubleshooting section
- Check database logs for errors

## 🔒 Security Notes

- Change default admin password immediately
- Use strong JWT secret keys in production
- Enable HTTPS in production
- Regular database backups recommended
- Monitor audit logs for suspicious activity

---

**Built with ❤️ for efficient Fixed Assets Management**
- **Containerization**: Docker & Docker Compose

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (optional)
- Node.js (for frontend development)

## 🔧 Installation

### Option 1: Docker Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fixed_assets_back
   ```

2. **Start the services**
   ```bash
   docker-compose up -d
   ```

3. **Initialize the database**
   ```bash
   docker-compose exec api python init_db.py
   ```

### Option 2: Manual Setup

1. **Clone and setup virtual environment**
   ```bash
   git clone <repository-url>
   cd fixed_assets_back
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup PostgreSQL database**
   ```sql
   CREATE DATABASE fixed_assets_management_db;
   CREATE USER belal WITH PASSWORD 'belal';
   GRANT ALL PRIVILEGES ON DATABASE fixed_assets_management_db TO belal;
   ```

4. **Configure environment**
   ```bash
   # Update config/app_local.cfg with your database settings
   ```

5. **Initialize database**
   ```bash
   python init_db.py
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

## 🚀 Usage

### API Access
- **API Base URL**: http://localhost:5000/api
- **API Documentation**: http://localhost:5000/docs/
- **pgAdmin**: http://localhost:8080 (admin@fixedassets.com / admin123)

### Default Admin Credentials
- **Username**: admin
- **Password**: Admin@123456

### API Endpoints

#### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - Register new user (admin only)
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/change-password` - Change password

#### Company Management
- `GET /api/companies` - List all companies
- `POST /api/companies` - Create new company
- `GET /api/companies/{id}` - Get company details
- `PUT /api/companies/{id}` - Update company
- `DELETE /api/companies/{id}` - Delete company

#### Assets Management
- `GET /api/assets` - List assets with filtering and pagination
- `POST /api/assets` - Create new asset
- `GET /api/assets/{id}` - Get asset details
- `PUT /api/assets/{id}` - Update asset
- `DELETE /api/assets/{id}` - Delete asset
- `GET /api/assets/statistics` - Asset statistics
- `GET /api/assets/search/{barcode}` - Search by barcode

#### Reports
- `GET /api/reports/assets` - Asset reports
- `GET /api/reports/financial` - Financial reports
- `GET /api/reports/maintenance` - Maintenance reports

## 📊 Database Schema

### Core Tables
- **companies** - Company information
- **branches** - Branch details linked to companies
- **warehouses** - Storage locations linked to branches
- **positions** - User roles/positions
- **permissions** - System permissions
- **users** - System users with authentication
- **asset_categories** - Asset categorization with depreciation rules
- **assets** - Main assets table with comprehensive tracking
- **asset_attachments** - File attachments for assets
- **asset_transfers** - Asset location transfer history
- **asset_maintenance** - Maintenance records and scheduling
- **audit_logs** - System audit trail
- **system_settings** - Configurable system parameters

### Key Relationships
- Company → Branches → Warehouses → Assets
- Users → Positions → Permissions (many-to-many)
- Assets → Categories, Branches, Warehouses
- Assets → Attachments, Transfers, Maintenance (one-to-many)

## 🔐 Permissions System

The system includes 25+ granular permissions organized by modules:

### Company & Structure
- `manage_company`, `view_company`
- `manage_branches`, `view_branches`
- `manage_warehouses`, `view_warehouses`

### User Management
- `manage_users`, `view_users`
- `manage_positions`, `view_positions`
- `manage_permissions`, `view_permissions`

### Asset Management
- `manage_assets`, `view_assets`, `delete_assets`
- `transfer_assets`, `manage_asset_categories`
- `manage_maintenance`, `view_maintenance`

### System Operations
- `generate_reports`, `export_data`
- `generate_barcodes`, `scan_barcodes`
- `upload_files`, `system_admin`

## 🐛 Development

### Running in Development Mode
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python main.py
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description of changes"

# Apply migration
alembic upgrade head

# View migration history
alembic history
```

### Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=modules
```

### Code Style
```bash
# Format code
black .

# Check imports
isort .

# Lint code
flake8 .
```

## 📈 Monitoring & Maintenance

### Logs
- Application logs: `logs/app.log`
- Error logs: `logs/error.log`
- Audit logs: Database table `audit_logs`

### Backups
- Database backups: `backups/`
- File uploads: `uploads/`
- Reports: `reports/`

### Health Checks
- API Health: `GET /health`
- Database connectivity check
- File system permissions check

## 🔒 Security Considerations

1. **Change default passwords** in production
2. **Configure proper JWT secrets**
3. **Set up HTTPS** with SSL certificates
4. **Regular database backups**
5. **Monitor audit logs** for suspicious activity
6. **Keep dependencies updated**
7. **Configure firewall rules**

## 🚀 Production Deployment

### Docker Production Setup
```bash
# Production docker-compose
docker-compose -f docker-compose.prod.yml up -d

# SSL setup with Let's Encrypt
certbot --nginx -d yourdomain.com
```

### Environment Variables
```bash
ENV=production
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact the development team
- Check the API documentation at `/docs/`

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

**Fixed Assets Management System** - Professional asset tracking and management solution.