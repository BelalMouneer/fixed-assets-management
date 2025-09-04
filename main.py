#!/usr/bin/env python3
"""
Fixed Assets Management System - Main Application Entry Point
"""

from modules.app import app
from modules.api import register_apis

if __name__ == '__main__':
    # Register all API blueprints
    register_apis()
    
    # Run the application
    app.run(
        host=app.config.get('HOST', '0.0.0.0'),
        port=app.config.get('PORT', 5000),
        debug=app.config.get('ENV') == 'development'
    )