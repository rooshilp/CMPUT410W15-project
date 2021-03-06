from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from nodes.models import Host
import urllib2

# Create your views here.

# EXAMPLES FOR OUR OWN HOST
def test(request):
    host = Host.objects.get(name="Group7")

    #response = host.get_posts_visible_to_current_user()
    #response = host.get_all_posts_by_author('eaec831d-9556-4a7f-b2c6-91e53cb6b437')

    response = host.get_public_posts()

    #response = host.get_postid('bff6366a-2614-4f16-9e51-45a8a3688679')

    #response = host.get_friend_response('eaec831d-9556-4a7f-b2c6-91e53cb6b437',
    #                                    'f859bdcd-f77c-41af-92e9-c769d04bb449')

    #response = host.post_friend_auth_response('eaec831d-9556-4a7f-b2c6-91e53cb6b437',
    #                                        ['f859bdcd-f77c-41af-92e9-c769d04bb449',
    #                                         'fe9ba287-de4a-48b3-b8e9-0bf216a7df81'])

    # eae is friend requester, fe9 is the one that eae is friend requesting to
    #response = host.post_friend_request(['eaec831d-9556-4a7f-b2c6-91e53cb6b437',
    #                                     'fe9ba287-de4a-48b3-b8e9-0bf216a7df81'])

    #response = host.get_all_authors()

    return JsonResponse(response, safe=False)
