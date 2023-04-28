from flask import session
from sqlalchemy import func
import logging
from . import db, cache
from .webmodels import Posts, Tags, post_tags
from .config import LOG_FORMAT, DATE_FORMAT
from datetime import timedelta
import random

NUMBER_OF_POPULAR = 3
NUMBER_OF_POPULAR_TAGS = 3


# configuring logging
logging.basicConfig(
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    level=logging.WARNING)

# configure werkzeug logger
wer_log = logging.getLogger('werkzeug')
wer_log.setLevel(logging.ERROR)

logger = logging.getLogger('routes')
logger.setLevel(logging.INFO)


def convert_created_time(*args, **kwargs):
    """
    Takes in post created date,
    returns this date in user time
    """
    result = ''
    try:
        timezone = session.get("timezone")
        sign = timezone[3]
        hours = int(timezone[4:6])
        minutes = int(timezone[7:])
        if sign == '+':
            delta = timedelta(hours=hours, minutes=minutes)
            result = args[0] + delta
        elif sign == '-':
            delta = timedelta(hours=-hours, minutes=-minutes)
            result = args[0] + delta
    except Exception as ex:
        logger.error(ex)
        result = args[0]
    return result.strftime('%d %B %Y, %H:%M')


# returns popular posts and tags for sidebar
@cache.cached(timeout=60)
def get_posts_and_tags():
    popular_posts = Posts.query.order_by(Posts.num_of_views.desc()).limit(NUMBER_OF_POPULAR).all()
    # request all the tags from DB
    tags = Tags.query.all()
    # randomize output of the tags
    shuffled_tags = random.sample(tags, len(tags))
    return popular_posts, shuffled_tags


# returns the most popular tags for footer
@cache.cached(timeout=60)
def get_popular_tags():
    result = db.session.query(Tags.tag_name, func.sum(Posts.num_of_views)). \
        select_from(Tags). \
        join(post_tags). \
        join(Posts). \
        group_by(Tags.id). \
        order_by(func.sum(Posts.num_of_views).desc()). \
        limit(NUMBER_OF_POPULAR_TAGS)
    return result
