# app.py
from flask import Flask
from routes import register_routes

app = Flask(__name__)

# Register all routes
register_routes(app)

if __name__ == "__main__":
    print("Starting Flask application...")
    app.run(debug=True, port=5000)


