from flask import session
from sqlalchemy import func
import logging
import random
from datetime import timedelta
import smtplib
from . import db
from .webmodels import Posts, Tags, post_tags
from .config import LOG_FORMAT, DATE_FORMAT
from .constants import EMAIL, APP_PASSWORD

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
def get_posts_and_tags():
    popular_posts = Posts.query.order_by(Posts.num_of_views.desc()).limit(NUMBER_OF_POPULAR).all()
    # request all the tags from DB
    tags = Tags.query.all()
    # randomize output of the tags
    shuffled_tags = random.sample(tags, len(tags))
    return popular_posts, shuffled_tags


# returns name and number of most popular tags for footer
def get_popular_tags():
    result = db.session.query(Tags.tag_name, func.count(Posts.id)). \
        select_from(Tags). \
        join(post_tags). \
        join(Posts). \
        group_by(Tags.id). \
        order_by(func.sum(Posts.num_of_views).desc()). \
        limit(NUMBER_OF_POPULAR_TAGS)
    return result


def send_email(name, email, subject, message):
    # email configuration
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    # create the email message
    msg = f"Subject: {subject}\n\nName: {name}\nEmail: {email}\n\n{message}"

    # send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(EMAIL, APP_PASSWORD)
        server.sendmail(EMAIL, EMAIL, msg)
