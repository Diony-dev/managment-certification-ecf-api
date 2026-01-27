from app import create_app
from config import config

import os
app = create_app(config[os.getenv('FLASK_CONFIG') or 'default'])

if __name__ == '__main__':
    app.run()
