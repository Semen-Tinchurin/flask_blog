from flask import Blueprint, flash, redirect, \
    url_for, render_template, request, session
from flask_login import login_required
import datetime
from . import db, cache
from .webmodels import Posts, Tags, Users
from .webforms import PostForm, TagForm, SearchForm, LoginForm, LetterForm
from .functions import convert_created_time, \
    logger, get_posts_and_tags, get_popular_tags, send_email

PAGINATION_NUM = 3
NUMBER_OF_LATEST = 3

bp = Blueprint('routes', __name__)

# routes that do not require authentication
allowed_routes = [
    'routes.index',
    'routes.contacts',
    'routes.get_post',
    'routes.login',
    'routes.single_post',
    'routes.search',
    'routes.posts_by_tag',
]


#
# @bp.before_request
# def require_login():
#     logger.info(request.endpoint, session.values())
#     if request.endpoint not in allowed_routes:
#         logger.info('requested page is not in allowed routes!!!')
#         if 'user_id' not in session:
#             logger.info('Redirecting to the login page...')
#             return redirect(url_for('routes.login'))
#         else:
#             logger.info('Redirecting to the admin page...')
#             return redirect(url_for(request.endpoint))


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
        logger.error('set timezone: ', ex)
        session['timezone'] = 'UTC -00:00'
    return timezone


@bp.route("/brick", methods=['GET', 'POST'])
def admin():
    if 'user_id' in session:
        logger.info('Went on the admin page')
        # request all the posts from DB
        posts = Posts.query.order_by(Posts.date_posted.desc())
        # counting posts
        number_of_posts = posts.count()
        # request all the tags from DB
        tags = Tags.query.all()
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
                               form=form)
    else:
        return redirect(url_for('routes.login'))


# add post page
@bp.route("/add-post", methods=['GET', 'POST'])
@login_required
def add_post():
    logger.info('Went on the add post page')
    form = PostForm()
    form.tags.choices = [(tag.id, tag.tag_name) for tag in Tags.query.all()]
    if form.validate_on_submit() and form.submit.data:
        try:
            post = Posts(title=form.title.data,
                         content=form.content.data,
                         slug=form.slug.data,
                         # image=,
                         tags=Tags.query.filter(Tags.id.in_(form.tags.data)).all())
            # clear the form
            form.title.data = ''
            form.content.data = ''
            form.slug.data = ''
            form.image.data = ''
            # add post data to database
            db.session.add(post)
            db.session.commit()
            # return a message
            flash('Post submitted successfully!')
            logger.info(f'Post {post.title} added')
        except Exception as ex:
            logger.error('app_post: ', ex)
        finally:
            return redirect(url_for('routes.admin'))
    elif form.validate_on_submit() and form.preview.data:
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
                               date_posted=date_posted)
    # redirect to the page
    return render_template('add_post.html', form=form)


# pass search form to navbar,
# popular posts and shuffled tags to sidebar
# and popular tags to footer
@bp.context_processor
def base():
    form = SearchForm()
    # creating context to pass convert_created_time function to the page
    context = {'convert': convert_created_time}
    tags_for_footer = get_popular_tags()
    popular_posts, shuffled_tags = get_posts_and_tags()
    return dict(form=form,
                tags_for_footer=tags_for_footer,
                popular_posts=popular_posts,
                shuffled_tags=shuffled_tags,
                **context)


@bp.route("/contacts", methods=['GET', 'POST'])
def contacts():
    form = LetterForm()
    if form.validate_on_submit():
        try:
            name = form.name.data
            email = form.email.data
            subject = form.subject.data
            message = form.message.data
            send_email(name=name, email=email, subject=subject, message=message)
            logger.info(f'User {name} sent an email')
            flash('Your message was sent to the admin!')
            form.name.data = ''
            form.email.data = ''
            form.subject.data = ''
            form.message.data = ''
        except Exception as ex:
            logger.error('contacts: ', ex)
            flash('Something gone wrong, try again...')
        finally:
            return render_template("contacts.html", form=form)
    return render_template("contacts.html", form=form)


@bp.route('/delete_<int:id>', methods=['GET', 'POST'])
@login_required
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
        logger.error('delete_post: ', ex)
        flash(f'Something is wrong! Error: {ex}')

    finally:
        return redirect(url_for('routes.admin'))


@bp.route('/delete_tag_<int:id>', methods=['GET', 'POST'])
@login_required
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
        logger.error('delete tag: ', ex)
        flash(f'Something is wrong! Error: {ex}')

    finally:
        return redirect(url_for('routes.admin'))


@bp.route('/edit_post_<int:id>', methods=['GET', 'POST'])
@login_required
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
    # request all the posts from DB
    posts = Posts.query
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
                           pages=pages)


@bp.route("/")
def index():
    logger.info('Went on site')
    # request last N posts
    posts = Posts.query.order_by(Posts.date_posted.desc()).limit(NUMBER_OF_LATEST)
    return render_template("index.html",
                           posts=posts)


@bp.errorhandler(500)
def internal_server_error(error):
    logger.error('INTERNAL SERVER ERROR 500')
    return render_template('500.html', title="INTERNAL SERVER ERROR"), 500


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.login.data
        password = form.password.data
        user = Users.query.filter_by(name=username).first()
        if user and user.verify_password(password=password):
            session['user_id'] = user.id
            flash('You are logged in as Admin')
            logger.info('Logged in as Admin')
            return redirect(url_for('routes.admin'))
        else:
            flash('Invalid username or password. Please try again.')
            return redirect(url_for('routes.login', form=form))
    form.login.data = ''
    form.password.data = ''
    return render_template('login.html', form=form)


@bp.route('/logout')
def logout():
    session.pop('user_id')
    return redirect(url_for('routes.index'))


# Custom 404 error page
@bp.errorhandler(404)
def page_not_found(error):
    logger.error('404 PAGE NOT FOUND')
    return render_template('404.html', title="PAGE NOT FOUND"), 404


@bp.route('/test1')
def test():
    slugs = Posts.query.with_entities(Posts.slug).all()
    return render_template('test_template.html',
                           result=slugs)


# page for single post
@bp.route("/posts/<slug>")
def single_post(slug):
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
                           prev_post=prev_post)


# search function
@bp.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Posts.query
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
                               posts=posts)
    else:
        return redirect(url_for('routes.index'))


@bp.route('/<tag>')
def posts_by_tag(tag):
    logger.info(f'Posts by tag {tag}')
    posts = Posts.query.filter(Posts.tags.any(tag_name=tag)).all()
    # requesting tags
    tags = Tags.query.all()
    return render_template('by_tag.html',
                           tag=tag,
                           posts=posts,
                           tags=tags)


@bp.route("/useful_stuff")
def useful_stuff():
    logger.info('Went on the useful page')
    return render_template('useful_stuff.html')
