from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, scoped_session
from modules import getpath
import os
import datetime

authorizations = {
  'Bearer Auth': {
    'type': 'apiKey',
    'in': 'header',
    'name': 'Authorization',
    'description': 'Enter your JWT Bearer token'
  }
}

app = Flask(__name__)

# Load the configuration from the config file
app.config.from_pyfile(getpath('/config/app_local.cfg'))

# Initialize JWT
jwt = JWTManager(app)

# Initialize Flask-RESTX
api = Api(
    app=app, 
    title='Fixed Assets Management System API',
    version='1.0',
    description='A comprehensive Fixed Assets Management System with role-based access control',
    security='Bearer Auth',
    authorizations=authorizations,
    doc='/docs/'  # Swagger UI location
)

# Configure CORS
if app.config['ENABLE_CORS']:
    CORS(app, resources={r'/*': {'origins': '*'}})

# Database connection
db_url = URL.create(
    app.config['DATABASE_DRIVER_NAME'],
    username=app.config['DATABASE_USERNAME'],
    password=app.config['DATABASE_PASSWORD'],
    host=app.config['DATABASE_HOST'],
    database=app.config['DATABASE_NAME'],
    port=app.config['DATABASE_PORT']
)

db_engine = create_engine(
    db_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=app.config.get('DEBUG', False)
)

# Create session factory
Session = scoped_session(sessionmaker(bind=db_engine))

# Configure upload directory
UPLOAD_FOLDER = app.config.get('UPLOAD_FOLDER', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Maximum file size (16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.teardown_appcontext
def remove_db_session(exception=None):
    """Remove database session after request"""
    Session.remove()

# Create database tables on first request (Flask 2.2+ compatible)
def create_tables():
    """Create database tables if they don't exist"""
    try:
        from modules.models.models import Base
        Base.metadata.create_all(db_engine)
    except Exception as e:
        # Database might not exist yet - this is handled by init_db.py
        pass

@app.route('/')
def index():
    """API root endpoint"""
    return {
        'message': 'Fixed Assets Management System API',
        'version': '1.0.0',
        'status': 'running',
        'documentation': '/docs/'
    }

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        session = Session()
        session.execute('SELECT 1')
        session.close()
        
        return {
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.datetime.utcnow().isoformat()
        }, 200
    except Exception as e:
        return {
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.datetime.utcnow().isoformat()
        }, 500
