from .. import create_app


def test_index_page():
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    flask_app = create_app()
    # create a test client using the Flask app
    with flask_app.test_client() as test_client:
        response = test_client.get('/')
        assert response.status_code == 200
        assert b'JunGuide' in response.data


def test_index_post_method():
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is posted to (POST)
    THEN check that a '405' status code is returned
    """
    flask_app = create_app()
    # create a test client using the Flask app
    with flask_app.test_client() as test_client:
        response = test_client.post('/')
        assert response.status_code == 405
        assert b'JunGuide' not in response.data
