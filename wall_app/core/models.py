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
