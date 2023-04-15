from .constants import *


# logging configuration
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
DATE_FORMAT = '%d.%m.%Y %I:%M:%S %p'


class Config:
    SECRET_KEY = SECRET_KEY
    # configuring the ckeditor
    CKEDITOR_SERVE_LOCAL = True
    CKEDITOR_ENABLE_CODESNIPPET = True
    CKEDITOR_CODE_THEME = 'monokai'
    CKEDITOR_PKG_TYPE = 'full'
    # configuring the database
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{USERNAME}:{DB_PASSWORD}@localhost/users'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
