# ABOUTME: WSGI entry point for production deployment with gunicorn or similar
# ABOUTME: Creates the Flask application instance for WSGI servers

import os
from dotenv import load_dotenv
from app import create_app

load_dotenv()

config_name = os.environ.get('FLASK_ENV', 'production')
app = create_app(config_name)

if __name__ == '__main__':
    app.run()
