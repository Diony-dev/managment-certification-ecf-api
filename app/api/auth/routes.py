from . import auth_bp

@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    return '<h1>Login</h1>'

