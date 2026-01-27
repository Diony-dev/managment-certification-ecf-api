import os
from dotenv import load_dotenv

class Config:
    load_dotenv()
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}
