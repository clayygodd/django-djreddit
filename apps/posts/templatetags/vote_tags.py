from django import template

from apps.posts.models import Comment

register = template.Library()

@register.filter(name='user_vote')
def user_vote(comment, user):
    return comment.get_user_vote(user).vote