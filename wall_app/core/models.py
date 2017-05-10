from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from accounts.models import Base


class Post(Base):
    """Represents posts on the app"""
    content = models.TextField()
    author = models.ForeignKey('auth.user', related_name='posts')

    class Meta:
        ordering = ('date_modified',)

    @staticmethod
    def get_queryset(user_id):
        """
        Returns a queryset of all Posts on the site

        This function appends to each object the field: in_love,
         which indicates whether the current user loves the post or not
        and the field: num_loves, which represents the number of
        loves the post has.

        Args:
            user_id -- the id of the current user
        """
        loves = Love.objects.filter(post=models.OuterRef('pk'), fan__id=user_id)
        qs = Post.objects.annotate(
            num_loves=models.Count('loves__post')).annotate(
                in_love=models.Exists(loves.values('id'))
        )
        return qs

    @staticmethod
    def order_queryset_by_num_loves(queryset, limit):
        return queryset.order_by('-num_loves')[0:limit]

    def __unicode__(self):
        return '{author} {date_created}'.format(
            author=self.author.username,
            date_created=self.date_created
        )


class Love(Base):
    fan = models.ForeignKey('auth.User', related_name='loves')
    post = models.ForeignKey('core.Post', related_name='loves')

    class Meta:
        unique_together = ('fan', 'post')

    @staticmethod
    def create_love(fan, post_id):
        """
        Creates a new love relationship between fan and post
        Args:
            fan -- a user object
            post_id -- a post id
        Returns:
            object created
        """
        post = Post.objects.get(id=post_id)
        love, created = Love.objects.get_or_create(fan=fan, post=post)
        return love

    @staticmethod
    def delete_love(fan, post_id):
        """
        Deletes a love relationship between fan and post
        Args:
            fan -- a user object
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
            fan=self.fan.username,
            post_id=self.post.id,
            author=self.post.author.username
        )
