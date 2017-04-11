from factories.factories import LoveFactory, PostFactory


def create_post_objects(user, num_posts):
    """Creates post objects
    Args:
        user -- the author of the posts
        num_posts -- number of posts to create

    Returns:
        list of posts
    """
    posts = []
    for post in xrange(num_posts):
        posts.append(PostFactory(author=user))
    return posts


def create_love_relationship(user, posts):
    """Creates a love relationship between a profile/user and a post
    Args:
        user -- user who is a fan of the post
        post -- a list of posts
    Returns:
        a list of loves
    """
    loves = []
    for post in posts:
        loves.append(LoveFactory(fan=user, post=post))
    return loves
