"""
Application entry point with environment setup
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set Flask app
os.environ.setdefault('FLASK_APP', 'run.py')

if __name__ == '__main__':
    from run import app
    app.run(debug=True)
