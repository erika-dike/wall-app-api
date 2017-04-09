from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db import models

from accounts.models import Base


class Post(Base):
    """Represents posts on the app"""
    content = models.TextField()
    owner = models.ForeignKey('accounts.Profile', related_name='posts')

    class Meta:
        ordering = ('date_modified',)

    def __unicode__(self):
        return '{owner} {date_created}'.format(
            owner=self.owner.user.username,
            date_created=self.date_created
        )


class Love(Base):
    fan = models.ForeignKey('accounts.Profile', related_name='loves')
    post = models.ForeignKey('core.Post', related_name='loves')

    class Meta:
        unique_together = ('fan', 'post')

    @staticmethod
    def create_love(fan, post_id):
        """
        Creates a new love relationship between fan and post
        Args:
            fan -- a profile object
            post_id -- a post id
        Returns:
            object created
        """
        try:
            post = Post.objects.get(id=post_id)
            love = Love.objects.create(fan=fan, post=post)
        except IntegrityError:
            love = Love.objects.get(fan=fan, post=post)
        return love

    @staticmethod
    def delete_love(fan, post_id):
        """
        Deletes a love relationship between fan and post
        Args:
            fan -- a profile object
            post_id -- a post id
        """
        try:
            post = Post.objects.get(id=post_id)
            Love.objects.get(fan=fan, post=post).delete()
        except ObjectDoesNotExist:
            pass

    @staticmethod
    def get_num_post_loves(post_id):
        """
        Returns the number of loves the post with the supplied post_id has
        """
        return Love.objects.filter(post__id=post_id).count()

    def __unicode__(self):
        return '{fan} loved post {post_id} by {author}'.format(
            fan=self.fan.user.username,
            post_id=self.post.id,
            author=self.post.owner.user.username
        )
