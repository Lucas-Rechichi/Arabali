import os

from django.shortcuts import render, HttpResponseRedirect
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from validate.forms import User
from django.contrib.auth.decorators import login_required
from main.models import Post
from main.forms import AddPost, EditProfile, EditPost
from main.models import LikedBy, Following
from main.models import UserStats
from django.http import HttpResponse
from django.conf import settings
from validate.views import create_user_directory
from main.errors import UsernameError
from main.configure import Configure
from datetime import datetime

# Create your views here.
def home(request):
    return render(request, "main/home.html")


@login_required
def page(request):
    name = request.user.username
    u = User.objects.get(username=name)
    us = UserStats.objects.get(user=u)
    p = Post.objects.all()
    s = UserStats.objects.all()
    post_users = {}
    for user_stat in s:
        post_users[str(user_stat.user.username)] = user_stat.pfp.url

    print (post_users)
    variables = {
        "username":name, 
        "post":p, 
        'user_stats':s, 
        'user':us,
        'post_users': post_users
    }
    

    return render(request, "main/page.html", variables)


@login_required
def add_post(request):
    username = request.user.username
    if request.method == "POST": # POST requests are encrypted, safer
        f = AddPost(request.POST, request.FILES) # enables the form for POST request
        print(request.POST, request.FILES)
        print("valid")
        username = request.user.username
        a = request.POST.get("title")
        c = request.POST.get("content")
        user = User.objects.get(username=username)
        user_stats = UserStats.objects.get(user=user)
        d = request.FILES.get("image")
        create_user_directory(user=user, sub_directory='posts')

        print(user_stats.pfp, d)
        b = Post(user=user, title=a, contents=c, likes=0, media=d, created_at=datetime.now())
        b.save()
        return HttpResponseRedirect("/page/")
    else:
        f = AddPost()
    return render(request, 'main/add_post.html', {"input_fields": f, 'username': username})

def liked(request):
    if request.method == 'POST':
        user = request.user.username
        post_id = request.POST.get('post_id')
        try:
            post = Post.objects.get(id=post_id)
            
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)
        if post.liked_by.filter(name=user).exists():
            liked_by = LikedBy.objects.get(name=user)
            post.likes -= 1
            post.liked_by.remove(liked_by)
        else:
            liked_by = LikedBy.objects.get(name=user)
            post.likes += 1
            post.liked_by.add(liked_by)
        post.save()
        return JsonResponse({'likes': post.likes})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def profile(request, name):
    u = User.objects.get(username=name)
    us = UserStats.objects.get(user=u)
    follow = Following.objects
    posts = Post.objects.filter(user=u)
    followed_userstats = []
    for x in follow.all():
        if us.following.filter(subscribers=x).exists():
            followed_userstats.append(UserStats.objects.filter(user=User.objects.get(username=follow.get(subscribers=x))))
    

    is_following = us.following.filter(subscribers=request.user.username).exists()

    if request.user.username == name:
        self_profile = True
    else:
        self_profile = False
    if request.method == 'POST':
        if 'follow' in request.POST:
            if request.POST['follow'] == 'follow':
                us.following.add(follow.get(subscribers=request.user.username))
                us.followers += 1
            elif request.POST['follow'] == 'unfollow':
                us.followers -= 1
                us.following.remove(follow.get(subscribers=request.user.username))
            us.save()
            is_following = us.following.filter(subscribers=request.user.username).exists()
            return HttpResponseRedirect(f'/profile/{u.username}')
    profile_vars = {
        'user': u, 
        'userstats': us, 
        'is_following': is_following, 
        'self_profile': self_profile, 
        'post': posts,
        'followed_user': followed_userstats, 
    }
    return render(request, 'main/profile.html', profile_vars)


def post_view(request, post_id):
    post = Post.objects.get(id=post_id)
    user = User.objects.get(username=post.user.username)
    user_stats = UserStats.objects.get(user=user)
    return render(request, 'main/posts.html', {"post": post, "user_stats": user_stats})

@login_required
def config(request, name):

    # Checking that the right user is acessing this page.
    username = request.user.username
    if name != username:
        return render(request, 'main/error.html', {'issue': 'Cannot access this users profile'})
    
    # Getting needed databace values
    user = User.objects.get(username=username)
    user_stats = UserStats.objects.get(user=user)

    # LikedBy Preperation
    user_posts = Post.objects.filter(user=user)
    post_list = list(user_posts)

    # Form init
    if request.method == 'POST':
        # Forms
        edit_profile_form = EditProfile(request.POST, request.FILES)
        edit_post_form = EditPost(request.POST, request.FILES)

        if request.POST.get('change'):
            if edit_profile_form.is_valid():
                # Form function
                edit_profile = Configure.edit_profile(request=request, current_username=username)
            
                # Editing Error Management
                if edit_profile in ['Cannot be named Images due to the default image directory being called Images.', 'Username Cannot Contain Spaces', 'Username Taken.']:
                    return render(request, 'main/error.html', {'issue': edit_profile})
            
                if edit_profile:
                    return HttpResponseRedirect(f'/edit/{edit_profile.username}')
        
        elif request.POST.get('delete'):
            for p in post_list:
                if int(request.POST.get('posts_id')) == int(p.pk):
                    Configure.delete_post(request=request, post=p)
                
        elif request.POST.get('confirm'):
            for p in post_list:
                if int(request.POST.get('post-id')) == int(p.pk):
                    Configure.edit_post(request=request, post=p)

        else:
            print('Other button pressed')
            print(request.POST)

    else:

        # Forms
        edit_profile_form = EditProfile()
        edit_post_form = EditPost()
          

    # LikedBy Preperation
    user_posts = Post.objects.filter(user=user)
    post_list = list(user_posts)

    variables = {
        'edit_profile_form': edit_profile_form,
        'edit_post_form': edit_post_form, 
        'user_stats': user_stats, 
        'username': username,
        'post': post_list,
    }        
    return render(request, 'main/config.html', variables)

def error(request, error):
    return render(request, 'main/error.html', {'issue':error})
    