"""
Main entry point for the Flask application
"""
import os
from app import create_app, get_mongo_db

# Create Flask app
app = create_app(config_name=os.getenv('FLASK_CONFIG', 'development'))


if __name__ == '__main__':
    # Run development server
    app.run(debug=True, host='127.0.0.1', port=5000)
