from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from accounts.models import Base

from .consumers import (
    send_post_delete_command_to_clients, send_love_status_to_clients,
    send_post_to_clients,
)


class Post(Base):
    """Represents posts on the app"""
    content = models.TextField()
    author = models.ForeignKey('auth.user', related_name='posts')

    class Meta:
        ordering = ('date_modified',)

    def __unicode__(self):
        return '{author} {date_created}'.format(
            author=self.author.username,
            date_created=self.date_created
        )

    def save(self, *args, **kwargs):
        """
        Hooking send_notification into the save of the object rather than
        use signals.
        """
        result = super(Post, self).save(*args, **kwargs)
        self.update_connected_users_on_save()
        return result

    def delete(self, *args, **kwargs):
        """
        Trigger the notifying of users on the websocket about the removal
        of models
        """
        post_id = self.id
        result = super(Post, self).delete(*args, **kwargs)
        Post.update_connected_users_on_delete(post_id)
        return result

    def update_connected_users_on_save(self):
        """
        Send a notification to everyone connected to our websocket
        of the post just created or updated
        """
        queryset = Post.get_queryset(None)
        post = queryset.filter(id=self.id)[0]
        send_post_to_clients(post)

    @staticmethod
    def update_connected_users_on_delete(post_id):
        """Send notification of delete on websocket channel"""
        send_post_delete_command_to_clients(post_id)

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
        loves = Love.objects.filter(post=models.OuterRef('pk'),
                                    fan__id=user_id)
        qs = Post.objects.annotate(
            num_loves=models.Count('loves__post')).annotate(
                in_love=models.Exists(loves.values('id'))
        ).order_by('-date_modified')
        return qs

    @staticmethod
    def order_queryset_by_num_loves(queryset, limit):
        return queryset.order_by('-num_loves')[0:limit]

    @staticmethod
    def filter_others_post(queryset, auth_user):
        """Returns posts authored by thte authenticated user

        Args:
            queryset -- queryset of all posts in the app
            auth_user -- the currently authenticated user
        """
        try:
            return queryset.filter(author=auth_user)
        except TypeError:
            return queryset


class Love(Base):
    fan = models.ForeignKey('auth.User', related_name='loves')
    post = models.ForeignKey('core.Post', related_name='loves')

    class Meta:
        unique_together = ('fan', 'post')

    def __unicode__(self):
        return '{fan} loved post {post_id} by {author}'.format(
            fan=self.fan.username,
            post_id=self.post.id,
            author=self.post.author.username
        )

    def update_connected_users(self):
        """
        Send updates to everyone connected to our websocket
        when object is created/updated
        """
        num_loves = Love.get_num_post_loves(self.post.id)
        payload = {
            'post_id': self.post.id,
            'num_loves': num_loves,
            'in_love': False,
        }
        send_love_status_to_clients(payload)

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
        love.update_connected_users()
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
            love = Love.objects.get(fan=fan, post=post)
            love.delete()
            love.update_connected_users()
        except ObjectDoesNotExist:
            pass

    @staticmethod
    def get_num_post_loves(post_id):
        """
        Returns the number of loves the post with the supplied post_id has
        """
        return Love.objects.filter(post__id=post_id).count()
