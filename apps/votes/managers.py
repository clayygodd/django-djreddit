from uuid import UUID
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Count, Sum


class VoteManager(models.Manager):
    def get_score(self, obj):
        """
        Get a dictionary containing the total score for ``obj`` and
        the number of votes it's received.
        """
        result = self.filter(comment_id=str(obj._get_pk_val())).aggregate(
            score=Sum("vote"), num_votes=Count("vote")
        )

        if result["score"] is None:
            result["score"] = 0
        return result

    def record_vote(self, comment, user, vote):
        """
        Record a user's vote on a given object. Only allows a given user
        to vote once, though that vote may be changed.
        A zero vote indicates that any existing vote should be removed.
        """
        if vote not in (1, 0, -1):
            raise ValueError("Invalid vote (must be +1/0/-1)")
        try:
            v = self.get(user=user, comment_id=str(comment._get_pk_val()))
            if vote == 0:
                v.delete()
            else:
                v.vote = vote
                v.save()
        except models.ObjectDoesNotExist:
            if vote == 0:
                return
            self.create(
                user=user, comment_id =str(comment._get_pk_val()), vote=vote
            )


    def get_user_vote(self, user, comment):
        try:
            vote = self.get(comment_id=comment._get_pk_val(), user=user)
        except models.ObjectDoesNotExist:
            vote = 0
        return vote