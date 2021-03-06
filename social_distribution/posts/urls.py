from django.conf.urls import patterns, include, url
from django.contrib import admin
from posts import views, api

urlpatterns = patterns('',
    url(r'^posts/$', views.posts, name='posts'),
    url(r'^author/(?P<author_id>.+)/posts/$', views.posts_by_author, name='author/author_id/posts'),
    url(r'^posts/all/$', views.public_posts, name='posts/all'),
    url(r'^delete/post/(?P<post_id>.+)$', views.delete_post, name='delete/post/post_id'),
    url(r'^edit/post/(?P<post_id>.+)$', views.edit_post, name='edit/post/post_id'),
    url(r'^posts/friends/$', views.friends_posts, name='posts/friends'),
    url(r'^posts/custom/$', views.custom_posts, name='posts/custom'),
    url(r'^posts/(?P<post_id>.+)/$',views.expand_post,name='expand_post'),
    url(r'^friends_posts/$',views.ajax_friends_post,name='friends_post'),
    url(r'^public_posts/$',views.ajax_public_posts,name='public_posts'),
    url(r'^posts_by_author/(?P<author_id>.+)$',views.ajax_posts_by_author,name='posts_by_author'),


    url(r'^api/author/posts/$', api.author_posts, name="api/author/posts"),
    url(r'^api/posts/$', api.posts, name="api/posts"),
    url(r'^api/author/(?P<author_id>.+)/posts/$', api.authorid_posts, name="api/author/author_id/posts"),
    url(r'^api/posts/(?P<post_id>.+)/$', api.postid_post, name="api/posts/post_id"),
    url(r'^api/friends/(?P<friend1>.+)/(?P<friend2>.+)/$', api.friends_get, name="api/friends_get"),
    url(r'^api/friends/(?P<uuid>.+)/$', api.friends_post, name="api/friends_post"),
    url(r'^api/friendrequest/$', api.friend_request, name="api/friendrequest"),
    url(r'^api/authors/$', api.authors, name="api/authors"),
    url(r'^api/post/$', api.post, name="api/post"),
    url(r'^api/foaf/$', api.foaf, name="api/foaf"),
)
