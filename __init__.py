from flask import Flask
from flask_admin import Admin
from flask_login import LoginManager
from flask_caching import Cache
from flask_ckeditor import CKEditor
from .webmodels import db, Users
from .config import Config
from flask_migrate import Migrate

# TODO Pattern matching, avoid of multiple else statements
# TODO test for only one user
# TODO check only existing tags in posts_by_tag func
# TODO fix and test convert time function
# TODO fix posts in russian
# TODO fix uploading image in post
# TODO thinc about Recent Reviews, You may also like and leave a reply
# TODO fix links in posts and sidebar
# TODO checking if admin
# TODO async functions

# https://codepen.io/ig_design/pen/omQXoQ
# https://support.sendwithus.com/jinja/jinja_time/
# https://www.free-css.com/free-css-templates/page244/tech-blog
# "https://www.digitalocean.com/community/tutorials/how-to-use-many-to-many-database-relationships-with-flask-sqlalchemy"

# Make migrations:
# export FLASK_ENV=development
# export FLASK_APP=blog.py
# flask db migrate -m 'message'
# flask db upgrade

cache = Cache()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    ckeditor = CKEditor(app)
    db.init_app(app)
    migrate = Migrate(app, db)
    from .webroutes import bp
    app.register_blueprint(bp)
    cache.init_app(app)
    admin = Admin(app)
    login_manager = LoginManager(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))

    return app


app = create_app()
