from flask import Flask
from .webmodels import db
from flask_ckeditor import CKEditor
from .config import Config
import logging


# configuring logging
FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
DATE_FORMAT = '%d.%m.%Y %I:%M:%S %p'
logging.basicConfig(
    format=FORMAT,
    datefmt=DATE_FORMAT,
    level=logging.WARNING)
# configure werkzeug logger
wer_log = logging.getLogger('werkzeug')
wer_log.setLevel(logging.ERROR)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    ckeditor = CKEditor(app)
    db.init_app(app)
    from .webroutes import cache
    cache.init_app(app)
    from .webroutes import bp
    app.register_blueprint(bp)
    return app


app = create_app()
