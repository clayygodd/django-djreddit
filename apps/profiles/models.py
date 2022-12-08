from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.posts.models import Category


class DjredditUser(AbstractUser):
    subscribed = models.ManyToManyField(Category)

    def get_subscribed(self):
        return self.subscribed.all()