# app/config.py 

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Konfigurasi dasar."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'nanti')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'nanti')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    GOOGLE_CLIENT_ID = os.getenv('nanti')  

class DevelopmentConfig(Config):
    """Konfigurasi untuk environment development."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///Inventory_dev.db')
    SQLALCHEMY_ECHO = True # Tampilkan query di console saat development
    CORS_ORIGINS = "*" # Izinkan semua origin untuk development

class ProductionConfig(Config):
    """Konfigurasi untuk environment production."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///main.db') # Wajib diset di production
    CORS_ORIGINS = os.getenv('FRONTEND_URL') # Wajib diset di production

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
