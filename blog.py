from flask import Flask, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_ckeditor import CKEditor
from flask_login import UserMixin, \
    login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from webforms import PostForm, SearchForm
from datetime import datetime
from configs import *

#
# TODO logging
# TODO async functions
# TODO checking if admin
# TODO fix links in posts and sidebar
# TODO cache navbar and footer

# https://codepen.io/ig_design/pen/omQXoQ
# https://support.sendwithus.com/jinja/jinja_time/
# https://www.free-css.com/free-css-templates/page244/tech-blog
# "https://www.digitalocean.com/community/tutorials/how-to-use-many-to-many-database-relationships-with-flask-sqlalchemy"

app = Flask(__name__)

app.config['CKEDITOR_SERVE_LOCAL'] = True
app.config['CKEDITOR_ENABLE_CODESNIPPET'] = True
app.config['CKEDITOR_CODE_THEME'] = 'monokai'
app.config['CKEDITOR_PKG_TYPE'] = 'full'
ckeditor = CKEditor(app)

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USERNAME}:{DB_PASSWORD}@localhost/users'
app.config['SECRET_KEY'] = SECRET_KEY

db = SQLAlchemy(app)
migrate = Migrate(app, db)

PAGINATION_NUM = 3
NUMBER_OF_LATEST = 3
NUMBER_OF_POPULAR = 3


# Make migrations:
# export FLASK_ENV=development
# export FLASK_APP=blog.py
# flask db migrate -m 'message'
# flask db upgrade


# many to many relationship
# post_tags = db.Table('post_tags',
#                      db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
#                      db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
#                      )


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow())
    slug = db.Column(db.String(100))
    num_of_views = db.Column(db.Integer, default=0)

    # tags = db.relationship('Tags',
    #                        secondary=post_tags,
    #                        lazy='subquery',
    #                        backref=db.backref('posts', lazy=True))

    def __repr__(self):
        return f'Post {self.title}'


#
# class Tags(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     tag_name = db.Column(db.String(50))
#
#     def __repr__(self):
#         return f'Tag {self.id} - {self.tag_name}'


@app.route("/brick")
def admin():
    posts = Posts.query.order_by(Posts.date_posted.desc())
    number_of_posts = posts.count()
    return render_template("adminpage.html", posts=posts, number_of_posts=number_of_posts)


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
    post_to_delete = Posts.query.get_or_404(id)
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash('Post deleted')

    except Exception as ex:
        flash(f'Something is wrong! Error: {ex}')

    finally:
        return redirect(url_for('admin'))


@app.route('/edit_post_<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.slug = form.slug.data
        # update database
        db.session.add(post)
        db.session.commit()
        flash("Post has been updated")
        return redirect(url_for('admin'))
    form.title.data = post.title
    form.content.data = post.content
    form.slug.data = post.slug
    return render_template('edit_post.html', form=form)


@app.route('/posts')
def get_posts():
    # grab all the posts from the database
    posts = Posts.query
    # adding pagination
    page = request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1
    pages = posts.paginate(page=page, per_page=PAGINATION_NUM)
    popular_posts = Posts.query.order_by(Posts.num_of_views.desc()).limit(NUMBER_OF_POPULAR)
    return render_template('posts.html',
                           posts=posts,
                           pages=pages,
                           popular_posts=popular_posts)


@app.route("/")
def index():
    posts = Posts.query.order_by(Posts.date_posted.desc()).limit(NUMBER_OF_LATEST)
    popular_posts = Posts.query.order_by(Posts.num_of_views.desc()).limit(NUMBER_OF_POPULAR)
    return render_template("index.html",
                           posts=posts,
                           popular_posts=popular_posts)


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html', title="INTERNAL SERVER ERROR"), 500


# Custom 404 error page
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', title="PAGE NOT FOUND"), 404


# page for single post
@app.route("/posts/<slug>")
def single_post(slug):
    post = Posts.query.filter_by(slug=slug).first()
    popular_posts = Posts.query.order_by(Posts.num_of_views.desc()).limit(NUMBER_OF_POPULAR)
    # counting views
    post.num_of_views += 1
    db.session.commit()
    return render_template("single_post.html",
                           post=post,
                           popular_posts=popular_posts)


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
    if form.validate_on_submit():
        # get data from submitted form
        searched = form.searched.data
        # query the database
        posts = posts.filter(Posts.content.like('%' + searched + '%'))
        posts = posts.order_by(Posts.date_posted.desc()).all()
        popular_posts = Posts.query.order_by(Posts.num_of_views.desc()).limit(NUMBER_OF_POPULAR)
        return render_template('search.html',
                               form=form,
                               searched=searched,
                               posts=posts,
                               popular_posts=popular_posts)
    else:
        return redirect(url_for('index'))


@app.route("/useful_stuff")
def useful_stuff():
    return render_template('useful_stuff.html')


if __name__ == "__main__":
    app.run(debug=True)
