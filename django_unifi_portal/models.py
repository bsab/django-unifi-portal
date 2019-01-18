from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class UnifiUser(models.Model):
    """Base module registered unifi user."""

    user = models.ForeignKey(User)
    picture = models.ImageField(upload_to='profile_images', default='profile_images/user_no_image.png',null=True)
    language = models.CharField(max_length=8, default='it-IT')  # aggiunto il 22/11/2016
    gender = models.CharField(max_length=10, null=True)
    city = models.CharField(max_length=200, null = True)
    about = models.CharField(max_length=255, null=True)
    dob = models.DateField(null=True)

    phone = models.CharField(max_length=255, null=True)
    guest_mac = models.CharField(max_length=255, null=True)
    last_backend_login = models.CharField(max_length=30, null=True)

    def __unicode__(self):
        return self.user.username

    def __str__(self):
        return self.user.username


    class Meta:
        app_label = 'django_unifi_portal'
        permissions = (
            ("can_navigate", "Can Navigate"),
        )

