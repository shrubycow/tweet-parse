from django.db import models

# Create your models here.
class TweetIds(models.Model):

    id = models.CharField(max_length=25, primary_key=True)
    likes = models.PositiveIntegerField(default=0)
    account = models.CharField(max_length=15)
    is_posted = models.BooleanField(default=False)