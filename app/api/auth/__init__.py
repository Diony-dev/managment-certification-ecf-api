from flask import Blueprint

# Creas el Blueprint
auth_bp = Blueprint('auth', __name__)

# Importas las rutas AQUÍ AL FINAL para evitar error circular
from . import routes