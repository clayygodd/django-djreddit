from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.views.generic import View, ListView, DetailView, CreateView, DeleteView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

from .models import Comment, Thread, Category
from .forms import NewCommentForm, NewThreadForm, NewCategoryForm


class TitleSearchMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            return queryset.filter(title__icontains=q)
        return queryset


class TestTemplate(TemplateView):
    template_name = "posts/test.html"


class CatListView(ListView):
    model = Category
    context_object_name = "categories"
    template_name = "category_list.html"


class CatCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = NewCategoryForm
    template_name = "posts/category_create.html"


class ThreadListBaseView(ListView):
    model = Thread
    context_object_name = "threads"
    template_name = "thread_list.html"

    class Meta:
        abstract = True


class ThreadListView(ThreadListBaseView):
    """
    Show all threads in category specific category.
    """
    def dispatch(self, request, *args, **kwargs):
        title = self.kwargs.get('title')
        self.category = get_object_or_404(Category, title=title)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class HomePageView(ThreadListBaseView):
    """
    A Show all subscribed threads if login, else show all threads.
    Show all threads if no subscribed category.
    """
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if user.is_authenticated and user.subscribed.all():
            subscribed = user.subscribed.all()
            queryset = queryset.filter(category__in=subscribed)
            return queryset
        else:
            return queryset


class ThreadDetailView(DetailView):
    """
    Thread detail page with all of its comments.
    """
    model = Thread
    context_object_name = "thread"
    template_name = "posts/thread_detail.html"

    def get_object(self):
        thread = get_object_or_404(Thread, slug=self.kwargs.get("comment_slug"))
        return thread

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        op = self.object.op
        all_comments = op.get_all_comments()
        context['allcomments'] = all_comments
        return context


class ThreadCreateView(LoginRequiredMixin, CreateView):
    model = Thread
    form_class = NewThreadForm
    template_name = "posts/thread_create.html"


    def get_initial(self):
        """Return the initial data to use for forms on this view."""
        category = self.kwargs.get("category")
        if category =="nocategory":
            return {}
        else:
            init_category = get_object_or_404(Category, title=category)
            return {"category":init_category}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = NewCommentForm
        return context


    def post(self, request, *args, **kwargs):
        thread_form = self.get_form()
        comment_form = NewCommentForm(data = request.POST)
        if thread_form.is_valid() and comment_form.is_valid():
            return self.form_valid(thread_form, comment_form)
        else:
            return HttpResponseRedirect(reverse_lazy("posts:thread_create"))

    def form_valid(self, thread_form, comment_form):
        comment_form.instance.created_by = self.request.user
        comment = comment_form.save()
        thread = thread_form.save(commit=False)
        thread.op = comment
        thread.save()
        return HttpResponseRedirect(thread.get_absolute_url())


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    template_name = "posts/reply.html"
    form_class = NewCommentForm

    def get_success_url(self):
        url = self.object.thread.get_absolute_url()
        return url

    def form_valid(self, form):
        pk = self.kwargs.get(self.pk_url_kwarg)
        parent = Comment.objects.get(id = pk)
        form.instance.parent = parent
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class CommentEditView(LoginRequiredMixin, UpdateView):
    model = Comment
    template_name = "posts/reply.html"
    form_class = NewCommentForm

    def get_success_url(self):
        url = self.object.thread.get_absolute_url()
        return url

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        comment = self.get_object()
        if comment.created_by == request.user:
            return response
        else:
            redirect_url = "/"
            return redirect(redirect_url)


class UserProfileView(LoginRequiredMixin, ListView):
    model = Thread
    template_name = "posts/user_profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ops = Comment.objects.filter(parent = None)
        username = self.kwargs.get("username")
        user_model = get_user_model()
        user = get_object_or_404(user_model, username = username)
        comments = Comment.objects.filter(created_by = user)
        votes = user.vote.all()
        context["threads"] = [ op.thread for op in ops if op.created_by == user]
        context["comments"] = [comment for comment in comments if comment.parent]
        context["upvotes"] = [i.comment for i in votes if i.vote==1]
        context["downvotes"] = [i.comment for i in votes if i.vote==-1]
        return context


class DjredditSearchView(ListView):
    model = Thread
    template_name = "posts/djreddit_search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get('q')
        if q:
            threads_q=Thread.objects.filter(title__icontains=q)
            categories_q = Category.objects.filter(title__icontains=q)
            comments_q = Comment.objects.filter(content__icontains=q)
            user = get_user_model()
            user_q = user.objects.filter(username__icontains=q)
            context["threads"] = [thread for thread in threads_q]
            context["categories"] = [category for category in categories_q]
            context["comments"] = [comment for comment in comments_q]
            context["users"] = [user for user in user_q]
            return context
        return context


class SubscriptionView(View):
    """Handle subscription post request"""

    def post(self, request, *args, **kwargs):
        sub = request.POST.get('sub')
        category_title = self.kwargs.get('category')
        category = get_object_or_404(Category, title=category_title)
        if request.user.is_authenticated:
            if sub=="subscribed":
                request.user.subscribed.add(category)
                return redirect("posts:thread_list", title = category.title)
            elif sub=="unsubscribed":
                request.user.subscribed.remove(category)
                return redirect("posts:homepage")
            else:
                return HttpResponse("<h1>post request not recognized</h1>")
        else:
            return redirect(reverse_lazy("account_login"))