"""
Configuração do Sistema de Rastreamento de QR Codes
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configurações base"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Database - SQLite local para desenvolvimento, PostgreSQL para produção
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')  # 'sqlite' ou 'postgresql'
    
    # SQLite
    SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', 'qrcode_tracking.db')
    
    # PostgreSQL/Supabase
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'qrcode_tracking')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Supabase (alternativa)
    SUPABASE_URL = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
    
    # API
    API_KEY = os.getenv('API_KEY', 'admin-api-key-change-me')
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Base URL do sistema
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def get_database_uri():
        """Retorna a URI do banco de dados baseado na configuração"""
        if Config.DATABASE_TYPE == 'sqlite':
            return f'sqlite:///{Config.SQLITE_DB_PATH}'
        else:
            return f'postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}'


class DevelopmentConfig(Config):
    """Configurações de desenvolvimento"""
    DEBUG = True
    DATABASE_TYPE = 'sqlite'


class ProductionConfig(Config):
    """Configurações de produção"""
    DEBUG = False
    DATABASE_TYPE = 'postgresql'


# Mapeamento de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

