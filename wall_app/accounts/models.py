from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


class Base(models.Model):
    """Base model for the database"""
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Profile(Base):
    """Represents a user on the site"""
    ACTIVE = 'ACTIVE'
    DELETED = 'DELETED'
    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (DELETED, 'Deleted')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.URLField(
        blank=True,
        default=('http://res.cloudinary.com/andela-troupon/image/upload/'
                 'v1491232845/default_profile_normal_n8yvkf.png')
    )
    about = models.CharField(max_length=20)
    email_confirmed = models.BooleanField(default=False)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=ACTIVE
    )

    def __unicode__(self):
        return '{user_name}'.format(user_name=self.user.username)
