from .conftest import NUMBER_OF_LATEST, NUMBER_OF_POPULAR, NUMBER_OF_POPULAR_TAGS, PAGINATION_NUM


def test_index(client):
    """
    #     GIVEN a Flask application configured for testing
    #     WHEN the '/' page is requested (GET)
    #     THEN check that the response is valid
    #     """
    response = client.get('/')
    number_of_posts = response.data.count(b'<div class="blog-box row">')
    assert response.status_code == 200
    assert b"JunGuide" in response.data
    assert b'<h1 align="center">Latest posts</h1>' in response.data
    assert number_of_posts == NUMBER_OF_LATEST


def test_index_post(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is posted to (POST)
    THEN check that a '405' status code is returned
    """
    response = client.post("/")
    assert response.status_code == 405
    assert b'JunGuide' not in response.data


def test_footer(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b'<footer class="footer">' in response.data
    assert b'About' in response.data
    assert b'Popular Tags' in response.data
    assert b'Contacts' in response.data


def test_header(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b'<header class="tech-header header">' in response.data
    assert b'Home' in response.data
    assert b'Posts' in response.data
    assert b'About' in response.data
    assert b'Contact Us' in response.data
    assert b'<form method="POST" action="/search" class="form-inline">' in response.data


def test_sidebar(client):
    response = client.get("/")
    assert response.status_code == 200
    # number_of_popular_posts = response.data.count(b'<div class="w-100 justify-content-between">')
    # assert number_of_popular_posts == NUMBER_OF_POPULAR
    assert b'Tags' in response.data
    assert b'Popular Posts' in response.data
    assert b'Recent Reviews' in response.data


def test_posts(client):
    response = client.get("/posts")
    posts = response.data.count(b'<div class="blog-box row">')
    assert response.status_code == 200
    assert b'<nav aria-label="Page navigation">' in response.data
    assert b'<h1 align="center">All Posts</h1>' in response.data
    assert posts == PAGINATION_NUM
