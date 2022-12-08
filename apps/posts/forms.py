from django import forms
from .models import Comment, Thread, Category
from mptt.forms import TreeNodeChoiceField


class NewCommentForm(forms.ModelForm):
    #parent = TreeNodeChoiceField(queryset=Comment.objects.all())

    class Meta:
        model = Comment
        fields = ('content',)

    def save(self, *args, **kwargs):
        Comment.objects.rebuild()
        return super(NewCommentForm, self).save(*args, **kwargs)


class NewThreadForm(forms.ModelForm):

    class Meta:
        model = Thread
        fields = ('title','category')


class NewCategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ('title','description')