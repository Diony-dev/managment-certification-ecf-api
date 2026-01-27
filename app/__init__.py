from flask import Flask
from app.api.auth import auth_bp
from app.api.ecf import ecf_bp
def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(ecf_bp, url_prefix='/ecf')
    return app
