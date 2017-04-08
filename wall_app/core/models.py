from __future__ import unicode_literals

from django.db import models

from accounts.models import Base


class Post(Base):
    """Represents messages on the app"""
    content = models.TextField()
    owner = models.ForeignKey('accounts.Profile', related_name='messages')

    class Meta:
        ordering = ('date_modified',)

    def __unicode__(self):
        return '{owner} {date_created}'.format(
            owner=self.owner.user.username,
            date_created=self.date_created
        )


# class Love(Base):
#     """Relates Messages to Users that love them"""
#     user = models.ForeignKey('auth.User', related_name='loves')
#     post = models.ForeignKey(
#         'Post',
#         on_delete=models.CASCADE,
#         related_name='loves'
#     )

#     class Meta:
#         unique_together = ('user', 'post')

#     def __unicode__(self):
#         return '{user} loves {post_id}'.format(
#             user=self.user.username,
#             post_id=self.post.id
#         )
