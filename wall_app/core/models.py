from __future__ import unicode_literals

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
