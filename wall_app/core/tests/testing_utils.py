from factories.factories import LoveFactory, PostFactory


def create_post_objects(profile, num_posts):
    """Creates post objects
    Args:
        profile -- the author of the posts
        num_posts -- number of posts to create

    Returns:
        list of posts
    """
    posts = []
    for post in xrange(num_posts):
        posts.append(PostFactory(author=profile))
    return posts


def create_love_relationship(profile, posts):
    """Creates a love relationship between a profile/user and a post
    Args:
        profile -- profile/user who is a fan of the post
        post -- a list of posts
    Returns:
        a list of loves
    """
    loves = []
    for post in posts:
        loves.append(LoveFactory(fan=profile, post=post))
    return loves
