from flask import Blueprint, flash, redirect, \
    url_for, render_template, request, session
from sqlalchemy import func
import datetime
from . import db, cache
from .webmodels import Posts, Tags, post_tags
from .webforms import PostForm, TagForm, SearchForm, LoginForm
from .functions import convert_created_time, logger, get_posts_and_tags
from .constants import ADMIN_LOG, ADMIN_PASS

PAGINATION_NUM = 3
NUMBER_OF_LATEST = 3
NUMBER_OF_POPULAR_TAGS = 3

bp = Blueprint('routes', __name__)


@bp.route('/timezone', methods=['POST'])
@cache.cached(timeout=60)
def set_timezone():
    """
    receives time zone from users browser
    in format "UTC+/-HH:MM"
    and returns time zone
    """
    timezone = ''
    try:
        timezone = request.json['timezone']
        session['timezone'] = timezone
        logger.info(timezone)
    except Exception as ex:
        logger.info(ex)
        session['timezone'] = 'UTC +0'
    return timezone


@bp.route("/brick", methods=['GET', 'POST'])
def admin():
    # creating context to pass convert_created_time function to the page
    context = {'convert': convert_created_time}
    logger.info('Went on the admin page')
    # request all the posts from DB
    posts = Posts.query.order_by(Posts.date_posted.desc())
    # counting posts
    number_of_posts = posts.count()
    # request all the tags from DB
    tags = Tags.query.all()
    # tags_with_post_count = db.session.query(Tags, func.count(Posts.id)). \
    #     select_from(Tags). \
    #     join(post_tags, Tags.id == post_tags.c.tag_id). \
    #     join(Posts, Posts.id == post_tags.c.post_id). \
    #     group_by(Tags.id). \
    #     order_by(Tags.tag_name).all()
    number_of_tags = len(tags)
    form = TagForm()
    if form.validate_on_submit():
        tag = Tags(tag_name=form.tag.data)
        form.tag.data = ''
        # saving new tag
        db.session.add(tag)
        db.session.commit()
        flash('Tag added!')
        logger.info(f'Tag {tag.tag_name} added')
        return redirect(url_for('routes.admin'))
    return render_template("adminpage.html",
                           posts=posts,
                           number_of_posts=number_of_posts,
                           tags=tags,
                           number_of_tags=number_of_tags,
                           form=form,
                           **context)


# add post page
@bp.route("/add-post", methods=['GET', 'POST'])
def add_post():
    logger.info('Went on the add post page')
    form = PostForm()
    form.tags.choices = [(tag.id, tag.tag_name) for tag in Tags.query.all()]
    if form.validate_on_submit() and form.submit.data:
        try:
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
            logger.info(f'Post {post.title} added')
        except Exception as ex:
            logger.error(ex)
        finally:
            return redirect(url_for('routes.admin'))
    elif form.validate_on_submit() and form.preview.data:
        # creating context to pass convert_created_time function to the page
        context = {'convert': convert_created_time}
        date_posted = datetime.datetime.utcnow()
        title = form.title.data
        content = form.content.data
        slug = form.slug.data
        tags = Tags.query.filter(Tags.id.in_(form.tags.data))
        logger.info(f'Preview post {title}')
        return render_template('preview.html',
                               title=title,
                               content=content,
                               tags=tags,
                               slug=slug,
                               date_posted=date_posted,
                               **context)
    # redirect to the page
    return render_template('add_post.html', form=form)


# pass stuff to navbar
@bp.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@bp.route("/contacts")
def contacts():
    return render_template("contacts.html")


@bp.route('/delete_<int:id>', methods=['GET', 'POST'])
def delete_post(id):
    logger.info('Went on the delete page')
    # request post that we need to delete
    post_to_delete = Posts.query.get_or_404(id)
    try:
        # deleting post
        db.session.delete(post_to_delete)
        db.session.commit()
        flash('Post deleted')
        logger.info(f'Post {post_to_delete.title} deleted')

    except Exception as ex:
        logger.error(ex)
        flash(f'Something is wrong! Error: {ex}')

    finally:
        return redirect(url_for('routes.admin'))


@bp.route('/delete_tag_<int:id>', methods=['GET', 'POST'])
def delete_tag(id):
    logger.info('Went on the delete tag page')
    # request tag that we need to delete
    tag_to_delete = Tags.query.get_or_404(id)
    try:
        # deleting tag
        db.session.delete(tag_to_delete)
        db.session.commit()
        flash('Tag deleted')
        logger.info(f'Tag {tag_to_delete.tag_name} deleted')

    except Exception as ex:
        logger.error(ex)
        flash(f'Something is wrong! Error: {ex}')

    finally:
        return redirect(url_for('routes.admin'))


@bp.route('/edit_post_<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    # request the post that we need to edit
    post = Posts.query.get_or_404(id)
    logger.info(f'Went on the edit post {post.title} page')
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
        logger.info(f'Post {post.title} was updated')
        return redirect(url_for('routes.admin'))
    # passing post data to the form
    form.title.data = post.title
    form.content.data = post.content
    form.slug.data = post.slug
    form.tags.data = selected_tags
    return render_template('edit_post.html', form=form)


@bp.route('/posts')
def get_posts():
    # creating context to pass convert_created_time function to the page
    context = {'convert': convert_created_time}
    # request all the posts from DB
    posts = Posts.query
    popular_posts, shuffled_tags = get_posts_and_tags()
    # adding pagination
    page = request.args.get('page')
    logger.info(f'Requested all posts page {page}')
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1
    pages = posts.paginate(page=page, per_page=PAGINATION_NUM)
    return render_template('posts.html',
                           posts=posts,
                           pages=pages,
                           popular_posts=popular_posts,
                           tags=shuffled_tags,
                           **context)


@bp.route("/")
def index():
    # creating context to pass convert_created_time function to the page
    context = {'convert': convert_created_time}
    logger.info('Went on site')
    popular_posts, shuffled_tags = get_posts_and_tags()
    # request last N posts
    posts = Posts.query.order_by(Posts.date_posted.desc()).limit(NUMBER_OF_LATEST)
    return render_template("index.html",
                           posts=posts,
                           tags=shuffled_tags,
                           popular_posts=popular_posts,
                           **context)


@bp.errorhandler(500)
def internal_server_error(error):
    logger.error('INTERNAL SERVER ERROR 500')
    return render_template('500.html', title="INTERNAL SERVER ERROR"), 500


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.login.data == ADMIN_LOG and form.password.data == ADMIN_PASS:
            flash('You are logged in as Admin')
            # app.logger.info('Logged in as Admin')
            return redirect(url_for('admin'))
    form.login.data = ''
    form.password.data = ''
    return render_template('login.html', form=form)


# Custom 404 error page
@bp.errorhandler(404)
def page_not_found(error):
    logger.error('404 PAGE NOT FOUND')
    return render_template('404.html', title="PAGE NOT FOUND"), 404


@bp.route('/test1')
def test():
    result = db.session.query(Tags.tag_name, func.sum(Posts.num_of_views)). \
        select_from(Tags). \
        join(post_tags). \
        join(Posts). \
        group_by(Tags.id). \
        order_by(func.sum(Posts.num_of_views).desc()). \
        limit(NUMBER_OF_POPULAR_TAGS)
    return render_template('test_template.html',
                           result=result)

# returns the most popular tags for footer
# def get_popular_tags():
#     pass


# page for single post
@bp.route("/posts/<slug>")
def single_post(slug):
    # creating context to pass convert_created_time function to the page
    context = {'convert': convert_created_time}
    # request wanted post
    post = Posts.query.filter_by(slug=slug).first()
    logger.info(f'Requested post - {post.title}')
    # request previous and next posts
    prev_post = Posts.query.filter(Posts.date_posted < post.date_posted).first()
    next_post = Posts.query.filter(Posts.date_posted > post.date_posted).first()
    # counting views
    post.num_of_views += 1
    # saving views
    db.session.commit()
    return render_template("single_post.html",
                           post=post,
                           next_post=next_post,
                           prev_post=prev_post,
                           **context)


# search function
@bp.route('/search', methods=['POST'])
def search():
    # creating context to pass convert_created_time function to the page
    context = {'convert': convert_created_time}
    form = SearchForm()
    posts = Posts.query
    popular_posts, shuffled_tags = get_posts_and_tags()
    if form.validate_on_submit():
        # get data from submitted form
        searched = form.searched.data
        logger.info(f'Searched for {searched}')
        # query the database
        posts = posts.filter(Posts.content.like('%' + searched + '%'))
        posts = posts.order_by(Posts.date_posted.desc()).all()
        return render_template('search.html',
                               form=form,
                               searched=searched,
                               posts=posts,
                               popular_posts=popular_posts,
                               tags=shuffled_tags,
                               **context)
    else:
        return redirect(url_for('index'))


@bp.route('/<tag>')
def posts_by_tag(tag):
    # creating context to pass convert_created_time function to the page
    context = {'convert': convert_created_time}
    logger.info(f'Posts by tag {tag}')
    posts = Posts.query.filter(Posts.tags.any(tag_name=tag)).all()
    popular_posts = get_posts_and_tags()[0]
    # requesting tags
    tags = Tags.query.all()
    return render_template('by_tag.html',
                           tag=tag,
                           posts=posts,
                           tags=tags,
                           popular_posts=popular_posts,
                           **context)


@bp.route("/useful_stuff")
def useful_stuff():
    logger.info('Went on the useful page')
    return render_template('useful_stuff.html')
