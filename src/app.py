# app.py
import os
from dotenv import load_dotenv
from flask import Flask
from routes import register_routes

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Register all routes
register_routes(app)

if __name__ == "__main__":
    print("Starting Flask application...")
    
    # Get configuration from environment variables
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    
    app.run(debug=debug_mode, host=host, port=port)