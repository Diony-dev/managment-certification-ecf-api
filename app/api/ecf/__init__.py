from flask import Blueprint

ecf_bp = Blueprint('ecf', __name__)

from . import routes
