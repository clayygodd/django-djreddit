from django import template
from django.urls import reverse


from apps.posts.forms import NewCommentForm
from apps.posts.models import Comment

register = template.Library()

@register.inclusion_tag('posts/reply.html')
def show_reply_form(action, id):
    if action == "reply":
        form_url = reverse('posts:comment_create', kwargs={'pk':id})
        form = NewCommentForm
    elif action == "edit":
        form_url = reverse('posts:comment_edit', kwargs={'pk': id})
        form = NewCommentForm(instance = Comment.objects.get(id = id))
    return {
            'form': form,
            'form_url':form_url
        }