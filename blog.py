from flask import Flask, render_template, flash, redirect, url_for, request, session
from flask_ckeditor import CKEditor
from flask_caching import Cache
import logging
import random
from datetime import datetime, timedelta
from webforms import PostForm, SearchForm, LoginForm, TagForm
from webmodels import *
from constants import *
from config import Config

# TODO fix 404 errors in single_post
# TODO popular categories in footer
# TODO fix posts in russian
# TODO image field for post model
# TODO fix links in posts and sidebar
# TODO checking if admin
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
app.config.from_object(Config)

# cache configuration
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

ckeditor = CKEditor(app)

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


# Make migrations:
# export FLASK_ENV=development
# export FLASK_APP=blog.py
# flask db migrate -m 'message'
# flask db upgrade

@app.route('/timezone', methods=['POST'])
def set_timezone():
    """
    receives time zone from users browser in format "UTC+/-HH:MM"
    and returns time zone
    """
    timezone = request.json['timezone']
    session['timezone'] = timezone
    app.logger.info(timezone)
    return timezone


def convert_created_time(time):
    """
    Takes in post created date,
    returns this date in user time
    """
    timezone = session.get("timezone")
    sign = timezone[3]
    hours = int(timezone[4:6])
    minutes = int(timezone[7:])
    if sign == '+':
        delta = timedelta(hours=hours, minutes=minutes)
        result = time + delta
    elif sign == '-':
        delta = timedelta(hours=-hours, minutes=-minutes)
        result = time + delta
    else:
        result = time
    return result


@app.route("/brick", methods=['GET', 'POST'])
def admin():
    app.logger.info('Went on the admin page')
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
        app.logger.info(f'Tag {tag.tag_name} added')
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
    app.logger.info('Went on the add post page')
    form = PostForm()
    form.tags.choices = [(tag.id, tag.tag_name) for tag in Tags.query.all()]
    if form.validate_on_submit():
        post = Posts(title=form.title.data,
                     content=form.content.data,
                     slug=form.slug.data,
                     tags=Tags.query.filter(Tags.id.in_(form.tags.data)).all())
        # clear the form
        form.title.data = ''
        form.content.data = ''
        form.slug.data = ''
        # add post data to database
        db.session.add(post)
        db.session.commit()
        # return a message
        flash('Post submitted successfully!')
        app.logger.info(f'Post {post.title} added')
        return redirect(url_for('admin'))
    # redirect to the page
    return render_template('add_post.html', form=form)


# pass stuff to navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@app.route("/contacts")
def contacts():
    return render_template("contacts.html")


@app.route('/delete_<int:id>', methods=['GET', 'POST'])
def delete_post(id):
    app.logger.info('Went on the delete page')
    # request post that we need to delete
    post_to_delete = Posts.query.get_or_404(id)
    try:
        # deleting post
        db.session.delete(post_to_delete)
        db.session.commit()
        flash('Post deleted')
        app.logger.info(f'Post {post_to_delete.title} deleted')

    except Exception as ex:
        app.logger.error(f'The ERROR occurred: {ex}')
        flash(f'Something is wrong! Error: {ex}')

    finally:
        return redirect(url_for('admin'))


@app.route('/delete_tag_<int:id>', methods=['GET', 'POST'])
def delete_tag(id):
    app.logger.info('Went on the delete tag page')
    # request tag that we need to delete
    tag_to_delete = Tags.query.get_or_404(id)
    try:
        # deleting tag
        db.session.delete(tag_to_delete)
        db.session.commit()
        flash('Tag deleted')
        app.logger.info(f'Tag {tag_to_delete.tag_name} deleted')

    except Exception as ex:
        app.logger.error(f'The ERROR occurred: {ex}')
        flash(f'Something is wrong! Error: {ex}')

    finally:
        return redirect(url_for('admin'))


@app.route('/edit_post_<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    # request the post that we need to edit
    post = Posts.query.get_or_404(id)
    app.logger.info(f'Went on the edit post {post.title} page')
    form = PostForm()
    selected_tags = [tag.id for tag in post.tags]
    form.tags.choices = [(tag.id, tag.tag_name) for tag in Tags.query.all()]
    if form.validate_on_submit():
        # passing post data from form to DB
        post.title = form.title.data
        post.content = form.content.data
        post.slug = form.slug.data
        post.tags = Tags.query.filter(Tags.id.in_(form.tags.data)).all()
        # update database
        db.session.add(post)
        db.session.commit()
        flash("Post has been updated")
        app.logger.info(f'Post {post.title} was updated')
        return redirect(url_for('admin'))
    # passing post data to the form
    form.title.data = post.title
    form.content.data = post.content
    form.slug.data = post.slug
    form.tags.data = selected_tags
    return render_template('edit_post.html', form=form)


@app.route('/posts')
def get_posts():
    app.logger.info('Requested all posts')
    # request all the posts from DB
    posts = Posts.query
    popular_posts, shuffled_tags = get_posts_and_tags()
    # adding pagination
    page = request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1
    pages = posts.paginate(page=page, per_page=PAGINATION_NUM)
    return render_template('posts.html',
                           posts=posts,
                           pages=pages,
                           popular_posts=popular_posts,
                           tags=shuffled_tags)


# returns popular posts and tags for sidebar
@cache.cached(timeout=60)
def get_posts_and_tags():
    popular_posts = Posts.query.order_by(Posts.num_of_views.desc()).limit(NUMBER_OF_POPULAR).all()
    # request all the tags from DB
    tags = Tags.query.all()
    # randomize output of the tags
    shuffled_tags = random.sample(tags, len(tags))
    return popular_posts, shuffled_tags


@app.route("/")
def index():
    app.logger.info('Went on site')
    # request last N posts
    posts = Posts.query.order_by(Posts.date_posted.desc()).limit(NUMBER_OF_LATEST)
    popular_posts, shuffled_tags = get_posts_and_tags()
    return render_template("index.html",
                           posts=posts,
                           popular_posts=popular_posts,
                           tags=shuffled_tags)


@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('INTERNAL SERVER ERROR 500')
    return render_template('500.html', title="INTERNAL SERVER ERROR"), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.login.data == ADMIN_LOG and form.password.data == ADMIN_PASS:
            flash('You are logged in as Admin')
            app.logger.info('Logged in as Admin')
            return redirect(url_for('admin'))
    form.login.data = ''
    form.password.data = ''
    return render_template('login.html', form=form)


# Custom 404 error page
@app.errorhandler(404)
def page_not_found(error):
    app.logger.error('404 PAGE NOT FOUND')
    return render_template('404.html', title="PAGE NOT FOUND"), 404


# preview page before saving post
# @app.route('/preview', methods=['POST'])
# def preview():
#     form = PostForm()
#     if form.validate():
#         post = Posts(title=form.title.data,
#                      content=form.content.data,
#                      slug=form.slug.data,
#                      tags=Tags.query.filter(Tags.id.in_(form.tags.data)))
#         app.logger.info(f'Preview post {post.title}')
#         return render_template('preview.html',
#                                post=post)


# page for single post
@app.route("/posts/<slug>")
def single_post(slug):
    # request wanted post
    post = Posts.query.filter_by(slug=slug).first()
    created_time = convert_created_time(post.date_posted)
    app.logger.info(f'Requested post - {post.title}')
    app.logger.info(created_time)
    # request previous and next posts
    prev_post = Posts.query.filter(Posts.date_posted < post.date_posted).first()
    next_post = Posts.query.filter(Posts.date_posted > post.date_posted).first()
    popular_posts, shuffled_tags = get_posts_and_tags()
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


# search function
@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Posts.query
    popular_posts, shuffled_tags = get_posts_and_tags()
    if form.validate_on_submit():
        # get data from submitted form
        searched = form.searched.data
        app.logger.info(f'Searched for {searched}')
        # query the database
        posts = posts.filter(Posts.content.like('%' + searched + '%'))
        posts = posts.order_by(Posts.date_posted.desc()).all()
        return render_template('search.html',
                               form=form,
                               searched=searched,
                               posts=posts,
                               popular_posts=popular_posts,
                               tags=shuffled_tags)
    else:
        return redirect(url_for('index'))


@app.route('/<tag>')
def posts_by_tag(tag):
    posts = Posts.query.filter(Posts.tags.any(tag_name=tag)).all()
    popular_posts = get_posts_and_tags()[0]
    # requesting tags
    tags = Tags.query.all()
    return render_template('by_tag.html',
                           tag=tag,
                           posts=posts,
                           tags=tags,
                           popular_posts=popular_posts)


@app.route("/useful_stuff")
def useful_stuff():
    app.logger.info('Went on the useful page')
    return render_template('useful_stuff.html')


if __name__ == "__main__":
    db.init_app(app)
    app.run(debug=True)
