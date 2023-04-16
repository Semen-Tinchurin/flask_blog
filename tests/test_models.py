import webmodels


def test_new_post():
    """
    GIVEN a Post model
    WHEN a new post is created
    THEN check if all fields created right
    """
    post = webmodels.Posts(title='Test post',
                 content='Some content',
                 slug='slg')
    assert post.title == 'Test post'
    assert post.content == 'Some content'
    assert post.slug == 'slg'


def test_new_tag():
    """
    GIVEN a Tags model
    WHEN a new tag is created
    THEN check if tag_name created right
    """
    tag = webmodels.Tags(tag_name='Test tag')
    assert tag.tag_name == 'Test tag'
