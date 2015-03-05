from django.shortcuts import render_to_response, render, redirect
from authors.forms import UserForm, UserProfileForm
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from authors.models import Profile, Follow
from django.contrib.auth.models import User
from django.db.models import Q

# Create your views here.
def index(request):
    context = RequestContext(request)
    list_of_users = User.objects.exclude( Q(username=request.user) | Q(username='admin'))

    return render(request, 'authors/index.html', {'list_of_users':list_of_users})


def register(request):
    context = RequestContext(request)

    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)


        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.is_active = False
            user.save()

            profile = Profile.create_profile(user)
            profile.host = request.get_host()
            profile.save()

            registered = True

        else:
            print user_form.errors

    else:
        user_form = UserForm()

    if registered == True:
        return HttpResponse("User successfully created! Login "
        "<a href=/login/>here</a> after the admin has activated your account.")
    else:
        return render_to_response('authors/register.html',
            {'user_form': user_form, 'registered': registered}, context)


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                return HttpResponse("This user has not been enabled by the admin yet.")
        else:
            print("Invalid login deatils: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'authors/login.html', {})

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

def author(request):
    context = RequestContext(request)

    return render(request, 'authors/author.html', {})

def author_manage(request):
    context = RequestContext(request)

    if request.method == 'POST':
        profile_form = UserProfileForm(data=request.POST)

        if profile_form.is_valid():
            profile.save()
        else:
            print profile_form.errors

    else:
        profile_form = UserProfileForm()

    if True:
        return HttpResponse("Profile Successfully edited! Click "
        "<a href=/author/>here</a> to return to your profile.")
    else:
        return render_to_response('authors/manage.html',
            {'profile_form': profile_form}, context)

#Profile
def profile(request, username):
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user_id = user.id)
    return render(request, 'authors/profile.html',{'profile':profile, 'user':user})

#Send Friend Request
def friend_request(request):
    if request.method == 'POST':
        to_profile_id = request.POST.get('to_profile','')
        current_profile = Profile.objects.get(user_id=request.user.id)
        to_profile = Profile.objects.get(id=to_profile_id)

        newFollow = Follow(from_profile_id=current_profile, to_profile_id=to_profile, status='PENDING')
        newFollow.save()
    return render(request, 'authors/index.html')

#Accept or Reject Friend Reject
def add_friend(request):
    current_profile = Profile.objects.get(user_id=request.user.id)

    if request.method == 'POST':
        from_profile_id = request.POST.get('from_profile', '')

        if 'accept' in request.POST:
            current_profile.friends.add(Profile.objects.get(id=from_profile_id))
            current_profile.save()

            #Remove from follow
            qs = Follow.objects.filter(from_profile_id=from_profile_id).filter(to_profile_id=current_profile.id)
            qs.delete()

        elif 'reject' in request.POST:
            #change status form PENDING to REJECT
            qs = Follow.objects.filter(from_profile_id=from_profile_id).filter(to_profile_id=current_profile.id).update(status='REJECTED')
        return redirect('index')
    else:
        qs = Follow.objects.filter(to_profile_id=current_profile.id).filter(status='PENDING')
        if qs:
            friends = qs
        else:
            friends = None
        return render(request, 'authors/add_friend.html',{'friends':friends})