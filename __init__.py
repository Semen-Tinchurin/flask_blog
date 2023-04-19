from flask import Flask
from flask_caching import Cache
from flask_ckeditor import CKEditor
from .webmodels import db
from .config import Config

# TODO fix 404 errors in single_post
# TODO popular categories in footer
# TODO fix posts in russian
# TODO image field for post model
# TODO fix links in posts and sidebar
# TODO checking if admin
# TODO async functions

# https://codepen.io/ig_design/pen/omQXoQ
# https://support.sendwithus.com/jinja/jinja_time/
# https://www.free-css.com/free-css-templates/page244/tech-blog
# "https://www.digitalocean.com/community/tutorials/how-to-use-many-to-many-database-relationships-with-flask-sqlalchemy"

cache = Cache()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    ckeditor = CKEditor(app)
    db.init_app(app)
    from .webroutes import bp
    app.register_blueprint(bp)
    cache.init_app(app)
    return app


app = create_app()
