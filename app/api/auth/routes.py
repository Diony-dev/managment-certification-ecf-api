from . import auth_bp
from app.services.auth.semilla_builder import SemillaBuilder
from flask import Response
@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    return '<h1 style="color: red;">Login</h1>'

@auth_bp.route('/semilla', methods=['POST', 'GET'])
def semilla():
    semillaXML = SemillaBuilder().get_xml_string()
    return Response(semillaXML, mimetype='application/xml')