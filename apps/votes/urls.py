from django.urls import path

from .views import request_vote_on_comment,TestTemplate


urlpatterns = [
    #path('vote/<str:direction>/<uuid:object_id>', request_vote_on_comment, name = "vote"),
    path('vote/ajax', request_vote_on_comment, name="vote"),
]