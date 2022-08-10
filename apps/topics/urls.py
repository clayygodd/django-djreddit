from django.urls import path, include

from .views import TopicListView

urlpatterns = [
    path('topic_list/', TopicListView.as_view(), name = "topic_list"),
]
