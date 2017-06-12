from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class UnifiUser(models.Model):
    """Base module registered unifi user."""

    user = models.ForeignKey(User)

    def __unicode__(self):
        return self.user.username

    def __str__(self):
        return self.user.username


    class Meta:
        app_label = 'unifi_portal'
        permissions = (
            ("can_navigate", "Can Navigate"),
        )

