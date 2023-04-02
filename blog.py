from flask import Flask, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_ckeditor import CKEditor
from flask_login import LoginManager, login_required, logout_user, current_user
from webforms import PostForm, SearchForm, LoginForm, TagForm
from datetime import datetime
import random
from configs import *

# TODO image field for post model
# TODO fix links in posts and sidebar
# TODO checking if admin
# TODO cache navbar and footer
# TODO logging
# TODO async functions

# https://codepen.io/ig_design/pen/omQXoQ
# https://support.sendwithus.com/jinja/jinja_time/
# https://www.free-css.com/free-css-templates/page244/tech-blog
# "https://www.digitalocean.com/community/tutorials/how-to-use-many-to-many-database-relationships-with-flask-sqlalchemy"

PAGINATION_NUM = 3
NUMBER_OF_LATEST = 3
NUMBER_OF_POPULAR = 3

app = Flask(__name__)

# configuring the ckeditor
app.config['CKEDITOR_SERVE_LOCAL'] = True
app.config['CKEDITOR_ENABLE_CODESNIPPET'] = True
app.config['CKEDITOR_CODE_THEME'] = 'monokai'
app.config['CKEDITOR_PKG_TYPE'] = 'full'
ckeditor = CKEditor(app)

# configuring the database
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USERNAME}:{DB_PASSWORD}@localhost/users'
app.config['SECRET_KEY'] = SECRET_KEY

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Make migrations:
# export FLASK_ENV=development
# export FLASK_APP=blog.py
# flask db migrate -m 'message'
# flask db upgrade


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


@app.route("/brick", methods=['GET', 'POST'])
def admin():
    # request all the posts from DB
    posts = Posts.query.order_by(Posts.date_posted.desc())
    # counting posts
    number_of_posts = posts.count()
    # request all the tags from DB
    tags = Tags.query.all()
    # counting tags
    number_of_tags = len(tags)
    # randomize output of the tags
    shuffled_tags = random.sample(tags, number_of_tags)
    form = TagForm()
    if form.validate_on_submit():
        tag = Tags(tag_name=form.tag.data)
        form.tag.data = ''
        # saving new tag
        db.session.add(tag)
        db.session.commit()
        flash('Tag added!')
        return redirect(url_for('admin'))
    return render_template("adminpage.html",
                           posts=posts,
                           number_of_posts=number_of_posts,
                           tags=shuffled_tags,
                           number_of_tags=number_of_tags,
                           form=form)


# add post page
@app.route("/add-post", methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(title=form.title.data,
                     content=form.content.data,
                     slug=form.slug.data)
        # clear the form
        form.title.data = ''
        form.content.data = ''
        form.slug.data = ''
        # add post data to database
        db.session.add(post)
        db.session.commit()
        # return a message
        flash('Post submitted successfully!')
        return redirect(url_for('admin'))
    # redirect to the page
    return render_template('add_post.html', form=form)


@app.route("/contacts")
def contacts():
    return render_template("contacts.html")


@app.route('/delete_<int:id>', methods=['GET', 'POST'])
def delete_post(id):
    # request post that we need to delete
    post_to_delete = Posts.query.get_or_404(id)
    try:
        # deleting post
        db.session.delete(post_to_delete)
        db.session.commit()
        flash('Post deleted')

    except Exception as ex:
        flash(f'Something is wrong! Error: {ex}')

    finally:
        return redirect(url_for('admin'))


@app.route('/edit_post_<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    # request the post that we need to edit
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        # passing post data from form to DB
        post.title = form.title.data
        post.content = form.content.data
        post.slug = form.slug.data
        # update database
        db.session.add(post)
        db.session.commit()
        flash("Post has been updated")
        return redirect(url_for('admin'))
    # passing post data to the form
    form.title.data = post.title
    form.content.data = post.content
    form.slug.data = post.slug
    return render_template('edit_post.html', form=form)


@app.route('/posts')
def get_posts():
    # request all the posts from DB
    posts = Posts.query
    # request all the tags from DB
    tags = Tags.query.all()
    # randomize output of the tags
    shuffled_tags = random.sample(tags, len(tags))
    # adding pagination
    page = request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1
    pages = posts.paginate(page=page, per_page=PAGINATION_NUM)
    # request popular posts for sidebar
    popular_posts = Posts.query.order_by(Posts.num_of_views.desc()).limit(NUMBER_OF_POPULAR)
    return render_template('posts.html',
                           posts=posts,
                           pages=pages,
                           popular_posts=popular_posts,
                           tags=shuffled_tags)


@app.route("/")
def index():
    # request last N posts
    posts = Posts.query.order_by(Posts.date_posted.desc()).limit(NUMBER_OF_LATEST)
    # request popular posts for sidebar
    popular_posts = Posts.query.order_by(Posts.num_of_views.desc()).limit(NUMBER_OF_POPULAR)
    tags = Tags.query.all()
    # randomize output of the tags
    shuffled_tags = random.sample(tags, len(tags))
    return render_template("index.html",
                           posts=posts,
                           popular_posts=popular_posts,
                           tags=shuffled_tags)


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html', title="INTERNAL SERVER ERROR"), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.login.data == ADMIN_LOG and form.password.data == ADMIN_PASS:
            flash('You are logged in as Admin')
            return redirect(url_for('admin'))
    form.login.data = ''
    form.password.data = ''
    return render_template('login.html', form=form)


# Custom 404 error page
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', title="PAGE NOT FOUND"), 404


# page for single post
@app.route("/posts/<slug>")
def single_post(slug):
    # request wanted post
    post = Posts.query.filter_by(slug=slug).first()
    # request previous and next posts
    prev_post = Posts.query.filter(Posts.date_posted < post.date_posted).first()
    next_post = Posts.query.filter(Posts.date_posted > post.date_posted).first()
    # request popular posts for sidebar
    popular_posts = Posts.query.order_by(Posts.num_of_views.desc()).limit(NUMBER_OF_POPULAR)
    # requestin tags
    tags = Tags.query.all()
    # randomize output of the tags
    shuffled_tags = random.sample(tags, len(tags))
    # counting views
    post.num_of_views += 1
    # saving views
    db.session.commit()
    return render_template("single_post.html",
                           post=post,
                           popular_posts=popular_posts,
                           tags=shuffled_tags,
                           next_post=next_post,
                           prev_post=prev_post)


# pass stuff to navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


# search function
@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Posts.query
    tags = Tags.query.all()
    # randomize output of the tags
    shuffled_tags = random.sample(tags, len(tags))
    if form.validate_on_submit():
        # get data from submitted form
        searched = form.searched.data
        # query the database
        posts = posts.filter(Posts.content.like('%' + searched + '%'))
        posts = posts.order_by(Posts.date_posted.desc()).all()
        # request popular posts for sidebar
        popular_posts = Posts.query.order_by(Posts.num_of_views.desc()).limit(NUMBER_OF_POPULAR)
        return render_template('search.html',
                               form=form,
                               searched=searched,
                               posts=posts,
                               popular_posts=popular_posts,
                               tags=shuffled_tags)
    else:
        return redirect(url_for('index'))


@app.route("/useful_stuff")
def useful_stuff():
    return render_template('useful_stuff.html')


if __name__ == "__main__":
    app.run(debug=True)
