
def test_index(client):
    """
    #     GIVEN a Flask application configured for testing
    #     WHEN the '/' page is requested (GET)
    #     THEN check that the response is valid
    #     """
    response = client.get('/')
    assert response.status_code == 200
    assert b"JunGuide" in response.data


def test_index_post(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is posted to (POST)
    THEN check that a '405' status code is returned
    """
    response = client.post("/")
    assert response.status_code == 405
    assert b'JunGuide' not in response.data
