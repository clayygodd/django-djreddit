from django.db import models

# Create your models here.
class Topic(models.Model):
    title = models.CharField(max_length = 20, blank = False, unique = True)
    description = models.CharField(max_length = 200, blank=True)

    def __str__(self):
        return self.title