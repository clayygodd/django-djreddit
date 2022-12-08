import json

from django.shortcuts import render
from django.apps import apps
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
)

from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext, loader
from django.views.generic import TemplateView


from apps.posts.models import Comment
from .models import Vote

VOTE_DIRECTIONS = (("up", 1), ("down", -1), ("clear", 0))


def json_error_response(error_message):
    return HttpResponse(json.dumps(dict(success=False, error_message=error_message)))



def request_vote_on_comment(request):
    """
    Generic object vote function for use via XMLHttpRequest.
    Properties of the resulting JSON object:
        success
            ``true`` if the vote was successfully processed, ``false``
            otherwise.
        score
            The object's updated score and number of votes if the vote
            was successfully processed.
        error_message
            Contains an error message if the vote was not successfully
            processed.
    """
    if not request.user.is_authenticated:
        return json_error_response("Not authenticated.")
    try:
        object_id = request.GET['object_id']
        direction = int(request.GET['direction'])
        obj = Comment._default_manager.get(id=object_id)
    except ObjectDoesNotExist:
        return json_error_response(f"No {Comment._meta.verbose_name} found for .")
    # Vote and respond
    Vote.vote_manager.record_vote(obj, request.user, direction)
    return HttpResponse(Vote.vote_manager.get_score(obj)["score"])


class TestTemplate(TemplateView):
    template_name = "votes/test.html"
