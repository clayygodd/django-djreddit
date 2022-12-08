import uuid
from slugify import slugify
from mptt.models import MPTTModel, TreeForeignKey

from django.db import models
from django.urls import reverse
from django.conf import settings

from apps.profiles.middleware import current_user
from apps.votes.models import Vote


def user_directory_path(instance, filename):
    return 'posts/%Y/%m/%d/'.format(instance.id, filename)


class Category(models.Model):
    title = models.CharField(max_length = 20, blank = False, unique = True)
    description = models.CharField(max_length = 200, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post:thread_list', args=[self.title])


class Thread(models.Model):
    title = models.CharField(max_length=70, blank=False)
    slug = models.SlugField(unique=False, null=True)
    url = models.URLField(max_length=120, blank=True, default='')
    views = models.IntegerField(blank=True, default=0)
    op = models.ForeignKey('Comment', related_name='+', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    locked = models.BooleanField(blank=True, default=False)
    is_stickied = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def _genSlug(self):
        slug = slugify(self.title, max_length=80)
        return slug

    def save(self, *args, **kwargs):
        self.slug = self._genSlug()
        super(Thread, self).save(*args, **kwargs)

    @property
    def relativeUrl(self):
        return reverse('post:thread_detail', args=[self.category.title, self.slug])

    def get_absolute_url(self):
        return self.relativeUrl


class Comment(MPTTModel):
    id = models.UUIDField(max_length=8, primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,)
    parent = TreeForeignKey('self', on_delete=models.CASCADE,
                            null=True, blank=True, related_name='children')
    content = models.TextField()
    publish = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now_add=False, auto_now=True)
    status = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ['publish']

    def __str__(self):
        return self.content[:70]

    @property
    def thread(self):
        comment = self
        while comment.parent:
            comment = comment.parent
        return Thread.objects.get(op=comment)

    def get_all_comments(self):
        """get all the comments in the current comment """
        comments = Comment.objects.filter(parent=self.id)
        for comment in comments:
            comments |= comment.get_all_comments()
        return comments

    def get_score(self):
        score = Vote.vote_manager.get_score(self)
        return score

    def get_user_vote(self, user):
        ''' return -1/0/1 if the comment is downvote/novote/upvote by the user'''
        return Vote.vote_manager.get_user_vote(user, self)


    #def get_uservote(self):
    #    """get the user's vote for the current user"""
    #    vote = Vote.objects




