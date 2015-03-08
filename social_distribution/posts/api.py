import json
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from authors.models import Profile, Follow
from django.contrib.auth.models import User
from posts.models import Post, Comment

def get_posts(posts):
    response_posts = []
    for post in posts:
        post_data = {}
        post_data['title'] = post.title
        post_data['source'] = ''
        post_data['origin'] = ''
        post_data['description'] = post.description
        post_data['content-type'] = post.content_type
        post_data['content'] = post.post_text
        post_data['author'] = {'id':post.author.uuid,'host':'',
        'displayname':post.author.displayname, 'url':''}
        post_data['categories'] = []
        post_data['comments'] = []

        for comment in Comment.objects.all():
            if comment.post_id.uuid == post.uuid:
                comment_data = {}
                comment_data['author'] = {'id':comment.author.uuid,
                'host':'', 'displayname':comment.author.displayname}
                comment_data['comment'] = comment.body
                comment_data['pubDate'] = comment.date
                comment_data['guid'] = comment.uuid
                post_data['comments'].append(comment_data)

        post_data['pubDate'] = post.date
        post_data['guid'] = post.uuid
        post_data['visibility'] = post.get_privacy_display()
        response_posts.append(post_data)

    return response_posts

# posts that are visible to the currently authenticated user
def author_posts(request):
    if request.method == "GET":
        post_list = []

        author_user = User.objects.get(username=request.user.username)
        author_profile = Profile.objects.get(user=author_user)
        all_posts = Post.objects.all()
        for post in all_posts:
            # Custom and public
            if author_user in post.allowed.all()\
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

# all posts marked as public on the server
def posts(request):
    if request.method == "GET":
        public_posts = Post.objects.filter(privacy=1)
        data = get_posts(public_posts)
        return JsonResponse(data, safe=False)

# all posts made by {AUTHOR_ID} visible to the currently authenticated user
def authorid_posts(request, author_id):
    if request.method == "GET":
        post_list = []

        author_profile = Profile.objects.get(uuid=author_id)
        author_posts = Post.objects.filter(author=author_profile)

        current_user = User.objects.get(username=request.user.username)
        current_profile = Profile.objects.get(user=current_user)

        for post in author_posts:
            # Custom and public
            if current_user in post.allowed.all()\
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

# access to a single post with id = {POST_ID}
def postid_post(request, post_id):
    if request.method == "GET":
        post = [Post.objects.get(uuid=post_id)]
        data = get_posts(post)
        return JsonResponse(data, safe=False)
"""http://127.0.0.1:8000/api/posts/305b5f7c-1c08-4b14-bb7c-9156b62a/"""

# a response if friends or not
def friends_get(request, friend1=None, friend2=None):
    if request.method == "GET":
        response = {}
        response['query'] = 'friends'
        response['friends'] = [friend1, friend2]

        isFriend = 'NO'
        try:
            friend1User = Profile.objects.get(uuid=friend1)
            for friend in friend1User.friends.all():
                if friend.uuid == friend2:
                    isFriend='YES'
        except:
            print("User does not exist")

        response['areFriends'] = isFriend
        return JsonResponse(response)

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
            print("User does not exist")

        response['friends'] = friends_list

        return JsonResponse(response)

        """
        curl -H "Content-Type:application/json" -d '{"query":"friends",
        "author":"72de3f1c-6645-46e8-b75e-48c4306c",
        "authors":[
        "ae254c4a-9888-4b48-9021-2e159d71886a",
        "9d61ed1d-7e14-4bbf-ba12-749b14c9fa94",
        "1d7e95e1-cd4d-4fb8-97b0-b42a0375b3c5",
        "e81e0cb8-c097-11e4-b10f-080027df60ad",
        "db0c413d-316f-443b-a696-8e3c4972112b",
        "72de3f1c-6645-46e8-b75e-48c4306c",
        "8485e927-8b76-45c7-b54c-51ee070d",
        "e81e0cb8-c097-11e4-b10f-080027df60ad"
        ]}' http://127.0.0.1:8000/api/friends/72de3f1c-6645-46e8-b75e-48c4306c/
        """

#XXX:TODO FOAF call
def foaf(request):
    return HttpResponse('test')


# to make a friend request POST to
@csrf_exempt
def friend_request(request):
    if request.method == "POST":
        received_data = json.loads(request.body)
        try:
            from_profile = Profile.objects.get(uuid=received_data['author']['id'])
            to_profile = Profile.objects.get(uuid=received_data['friend']['author']['id'])
        except:
            return HttpResponse("User does not exist")

        try:
            newFollow = Follow(from_profile_id=from_profile, to_profile_id=to_profile, status='PENDING')
            newFollow.save()
        except:
            return HttpResponse("Following failed")

        return HttpResponse(status=200)


    """
    curl -H "Content-Type: application/json" -d '{"query":"friendrequest", "author":{"id":"72de3f1c-6645-46e8-b75e-48c4306c", "host":"http://127.0.0.1:8000/", "displayname":"Greg"}, "friend": {"author":{"id":"1d7e95e1-cd4d-4fb8-97b0-b42a0375b3c5", "host":"http://127.0.0.1:5454/", "displayname":"Lara", "url":"http://127.0.0.1:5454/author/1d7e95e1-cd4d-4fb8-97b0-b42a0375b3c5"}}}' http://127.0.0.1:8000/api/friendrequest
    """