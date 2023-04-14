from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from blog import app

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# many to many relationship for Posts ang Tags models
post_tags = db.Table('post_tags',
                     db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
                     db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
                     )


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow())
    slug = db.Column(db.String(100))
    num_of_views = db.Column(db.Integer, default=0)

    tags = db.relationship('Tags',
                           secondary=post_tags,
                           lazy='subquery',
                           backref=db.backref('posts', lazy=True))

    def __repr__(self):
        return f'Post {self.title}'


class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(50))

    def __repr__(self):
        return f'Tag {self.id} - {self.tag_name}'


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    color = db.Column(db.String(50))
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return self.name
