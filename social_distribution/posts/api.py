import json
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
from authors.models import Profile, Follow
from django.contrib.auth.models import User
from posts.models import Post, Comment

def get_posts(posts):
    response_posts = []
    for post in posts:
        post_data = {}
        post_data['title'] = post.title
        post_data['source'] = 'http://cs410.cs.ualberta.ca:41024'
        post_data['origin'] = 'http://cs410.cs.ualberta.ca:41024'
        post_data['description'] = post.description
        post_data['content-type'] = post.content_type
        post_data['content'] = post.post_text
        post_data['author'] = {'id':post.author.uuid,
        'host':post.author.host,
        'displayname':post.author.displayname,
        'url':"http://cs410.cs.ualberta.ca:41024/author/" + post.author.uuid}
        post_data['categories'] = []
        post_data['comments'] = []

        for comment in Comment.objects.all():
            if comment.post_id.uuid == post.uuid:
                comment_data = {}
                comment_data['author'] = {'id':comment.author.uuid,
                'host':post.author.host, 'displayname':comment.author.displayname}
                comment_data['comment'] = comment.body
                comment_data['pubDate'] = comment.date
                comment_data['guid'] = comment.uuid
                post_data['comments'].append(comment_data)

        post_data['pubDate'] = post.date
        post_data['guid'] = post.uuid
        post_data['visibility'] = post.get_privacy_display()
        response_posts.append(post_data)
    response_json = {'posts':response_posts}

    return response_json

# posts that are visible to the currently authenticated user
def author_posts(request):
    if request.method == "GET":
        post_list = []
        if request.user.is_authenticated():
            author_user = User.objects.get(username=request.user.username)
            author_profile = Profile.objects.get(user=author_user)
            all_posts = Post.objects.all()
            for post in all_posts:
                # Custom and public
                if author_profile in post.allowed.all()\
                 or post.get_privacy_display() == 'Public':
                    post_list.append(post)

                # Private
                if post.get_privacy_display() == 'Private'\
                and post.author == author_profile:
                    post_list.append(post)

                # Friends
                if post.get_privacy_display() == "Friends":
                    if author_profile in post.author.friends.all():
                        post_list.append(post)

            data = get_posts(post_list)
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse(post_list, safe=False)
    return HttpResponse(status=405)

# all posts marked as public on the server
def posts(request):
    if request.method == "GET":
        public_posts = Post.objects.filter(privacy=1)
        data = get_posts(public_posts)
        return JsonResponse(data, safe=False)
    return HttpResponse(status=405)

"""curl -u username:password http://cs410.cs.ualberta.ca:41024/api/posts/"""

# all posts made by {AUTHOR_ID} visible to the currently authenticated user
@login_required
def authorid_posts(request, author_id):
    if request.method == "GET":
        post_list = []

        try:
            author_profile = Profile.objects.get(uuid=author_id)
            author_posts = Post.objects.filter(author=author_profile)

            current_user = User.objects.get(username=request.user.username)
            current_profile = Profile.objects.get(user=current_user)
        except:
            return HttpResponse(status=404)

        for post in author_posts:
            # Custom and public
            if current_profile in post.allowed.all()\
             or post.get_privacy_display() == 'Public':
                post_list.append(post)

            # Private
            if post.get_privacy_display() == 'Private'\
            and post.author == current_profile:
                post_list.append(post)

            # Friends
            if post.get_privacy_display() == "Friends":
                if current_profile in post.author.friends.all():
                    post_list.append(post)

        data = get_posts(post_list)
        return JsonResponse(data, safe=False)
    return HttpResponse(status=405)

# access to a single post with id = {POST_ID}
def postid_post(request, post_id):
    # get post with id in url
    if request.method == "GET":
        try:
            post = [Post.objects.get(uuid=post_id)]
            data = get_posts(post)
        except:
            return HttpResponse(status=404)
        return JsonResponse(data, safe=False)
    # update post with id in url
    if request.method == "PUT":
        received_data = json.loads(request.body)
        try:
            current_user = User.objects.get(username=request.user.username)
            current_profile = Profile.objeects.get(user=current_user)
            post = Post.objects.get(uuid=post_id)

            title = received_data['title']
            description = received_data['description']
            content_type = received_data['content-type']
            content = received_data['content']

            post.title = received_data['title']
            post.description = received_data['description']
            post.content_type = received_data['content-type']
            post.post_text = received_data['content']
            post.save()
        except:
            return HttpResponse(status=404)

        return HttpResponse(status=200)

    # create post with id in url
    if request.method == "POST":
        received_data = json.loads(request.body)
        try:
            current_user = User.objects.get(username=request.user.username)
            current_profile = Profile.objects.get(user=current_user)

            title = received_data['title']
            description = received_data['description']
            content_type = received_data['content-type']
            content = received_data['content']
            date = timezone.now()
            new_post = Post(uuid=post_id, author=current_profile, title=title, description=description,
            content_type=content_type, post_text=content, date=date)
            new_post.save()
        except:
            return HttpResponse(status=404)

        return HttpResponse(status=200)

    return HttpResponse(status=405)
"""http://127.0.0.1:8000/api/posts/305b5f7c-1c08-4b14-bb7c-9156b62a/"""

@login_required
def post(request):
    if request.method == "POST":
        received_data = json.loads(request.body)
        try:
            current_user = User.objects.get(username=request.user.username)
            current_profile = Profile.objects.get(user=current_user)

            title = received_data['title']
            description = received_data['description']
            content_type = received_data['content-type']
            content = received_data['content']
            date = timezone.now()
            new_post = Post(author=current_profile, title=title, description=description,
            content_type=content_type, post_text=content, date=date)
            new_post.save()
        except:
            return HttpResponse(status=500)

        return HttpResponse(status=200)

    return HttpResponse(status=405)

# a response if friends or not
def friends_get(request, friend1=None, friend2=None):
    if request.method == "GET":
        response = {}
        response['query'] = 'friends'
        response['authors'] = [friend1, friend2]

        isFriend = 'NO'
        try:
            friend1User = Profile.objects.get(uuid=friend1)
            for friend in friend1User.friends.all():
                if friend.uuid == friend2:
                    isFriend='YES'
        except:
            return HttpResponse(status=404)

        response['friends'] = isFriend
        return JsonResponse(response)
    return HttpResponse(status=405)

# ask if anyone in the list is a friend
@csrf_exempt
def friends_post(request, uuid):
    if request.method == "POST":
        response = {}
        friends_list = []
        response['query'] = 'friends'
        response['author'] = uuid

        received_data = json.loads(request.body)
        try:
            user = Profile.objects.get(uuid=uuid)
            friends_unicode = user.friends.all().values('uuid')
            friends = []
            for friend in friends_unicode:
                friends.append(friend['uuid'])

            for author in received_data['authors']:
                if author in friends:
                    friends_list.append(author)

        except:
            return HttpResponse(status=404)

        response['friends'] = friends_list

        return JsonResponse(response)

    return HttpResponse(status=405)

"""
curl -H "Content-Type:application/json" -u user:pass http://127.0.0.1:8000/api/friends/eaec831d-9556-4a7f-b2c6-91e53cb6b437/ -d '{"query":"friends","author":"eaec831d-9556-4a7f-b2c6-91e53cb6b437","authors":["f859bdcd-f77c-41af-92e9-c769d04bb449","fe9ba287-de4a-48b3-b8e9-0bf216a7df81"]}'
"""

@csrf_exempt
def foaf(request):
    if request.method == "POST":
        received_data = json.loads(request.body)
        try:
            requested_author = received_data['id']
            requesting_author = received_data['author']['id']
            friends_list = received_data['friends']
        except:
            return HttpResponse(status=400)

        post_list = []
        requester = Profile.objects.get(uuid=requesting_author)
        requestee = Profile.objects.get(uuid=requested_author)
        requester_friends = requester.friends.all()
        for friend in friends_list:
            friend_profile = Profile.objects.get(uuid=friend)
            if friend_profile in requester_friends:
                author_posts = Post.objects.filter(author=requestee)
                for post in author_posts:
                    post_list.append(post)
                response = get_posts(post_list)

                return JsonResponse(response)

    return HttpResponse(status=405)

"""
curl -H "Content-Type:application/json" -u user:pass 127.0.0.1:8000/api/foaf/ -d '{"query":"getpost","id":"fe9ba287-de4a-48b3-b8e9-0bf216a7df81","author":{"id":"eaec831d-9556-4a7f-b2c6-91e53cb6b437","host":"http://127.0.0.1:8000","displayname":"User1"},"friends":["f859bdcd-f77c-41af-92e9-c769d04bb449"]}'
"""


# to make a friend request POST to
@csrf_exempt
def friend_request(request):
    if request.method == "POST":
        received_data = json.loads(request.body)
        try:
            from_profile = Profile.objects.get(uuid=received_data['author']['id'])
        except:
            from_user = User(username=received_data['author']['displayname']+"@"+received_data['author']['host'],
                            password="")
            from_user.save()
            from_profile = Profile.objects.create(user=from_user,uuid=received_data['author']['id'],
            displayname=received_data['author']['displayname'])

        try:
            to_profile = Profile.objects.get(uuid=received_data['friend']['id'])
        except:
            return HttpResponse(status=404)

        try:
            checkFollow = Follow.objects.filter( Q(from_profile_id=from_profile) & Q(to_profile_id=to_profile) ).first()
            if not checkFollow:
                newFollow = Follow(from_profile_id=from_profile, to_profile_id=to_profile, status='PENDING')
                newFollow.save()
        except:
            return HttpResponse(status=500)

        return JsonResponse('Success!', safe=False)
    return HttpResponse(status=405)


    """
    curl -H "Content-Type: application/json" -d '{"query":"friendrequest", "author":{"id":"72de3f1c-6645-46e8-b75e-48c4306c", "host":"http://127.0.0.1:8000/", "displayname":"Greg"}, "friend": {"author":{"id":"1d7e95e1-cd4d-4fb8-97b0-b42a0375b3c5", "host":"http://127.0.0.1:5454/", "displayname":"Lara", "url":"http://127.0.0.1:5454/author/1d7e95e1-cd4d-4fb8-97b0-b42a0375b3c5"}}}' http://127.0.0.1:8000/api/friendrequest
    """

def authors(request):
    if request.method == "GET":
        response = []
        all_authors = Profile.objects.all()
        for author in all_authors:
            author_data = {}
            author_data['username'] = author.user.username
            author_data['id'] = author.uuid
            author_data['host'] = author.host
            author_data['displayname'] = author.displayname
            author_data['url'] = author.host + "/author/" + author.user.username
            response.append(author_data)

        return JsonResponse(response, safe=False)

    return HttpResponse(status=405)
