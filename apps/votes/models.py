from django.db import models
from django.conf import settings

#from apps.posts.models import Comment
from .managers import VoteManager

#from django.apps import apps
#Comment = apps.get_model('apps.posts','Comment')

SCORES = (
    (+1, "+1"),
    (-1, "-1"),
)

class Vote(models.Model):
    """
    A vote on Comment by a User.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vote")
    comment = models.ForeignKey('posts.Comment', on_delete=models.CASCADE, related_name="vote")
    vote = models.SmallIntegerField(choices=SCORES)

    objects = models.Manager()
    vote_manager = VoteManager()

    class Meta:
        db_table = "votes"
        # One vote per user per object
        unique_together = (("user", "comment","comment_id"),)

    def __str__(self):
        return f"{self.user}: {self.vote} on {self.comment}"

    def is_upvote(self):
        return self.vote == 1

    def is_downvote(self):
        return self.vote == -1