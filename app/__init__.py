from flask import Flask
from app.api.auth import auth_bp
from app.api.ecf import ecf_bp
from flask_cors import CORS

def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize CORS
    CORS(app)

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(ecf_bp, url_prefix='/ecf')
    return app
