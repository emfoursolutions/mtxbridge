# ABOUTME: Main application entry point for Flask development server
# ABOUTME: Creates the Flask app instance and runs it in debug mode

import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv()

# Create Flask app
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    app.run(
        host=os.environ.get('FLASK_HOST', '0.0.0.0'),
        port=int(os.environ.get('FLASK_PORT', 8000)),
        debug=config_name == 'development'
    )
