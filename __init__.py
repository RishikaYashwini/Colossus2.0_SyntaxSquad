from flask import Flask
from app.config.firebase_config import initialize_firebase
from app.api import init_api

def create_app():
    app = Flask(__name__)
    
    # Initialize Firebase
    db = initialize_firebase()
    
    # Register API blueprint
    api_blueprint = init_api(db)
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    @app.route('/')
    def index():
        return {
            "name": "CultureCoin API",
            "version": "1.0.0",
            "description": "API for CultureCoin, a digital currency system that supports local businesses"
        }
    
    return app