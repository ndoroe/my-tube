#!/usr/bin/env python3
"""
MyTube Backend Application Entry Point
"""
import os
from app import create_app, make_celery

# Create Flask application
app = create_app()

# Create Celery instance
celery = make_celery(app)

if __name__ == '__main__':
    # Development server
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
