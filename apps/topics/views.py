from django.shortcuts import render
from django.views.generic.list import ListView

from .models import Topic


class TopicListView(ListView):
    model = Topic
    context_object_name = "topics"
    template_name = "topic_list.html"