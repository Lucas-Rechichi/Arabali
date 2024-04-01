from django.shortcuts import render, HttpResponseRedirect
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from validate.forms import User
from django.contrib.auth.decorators import login_required
from main.models import Post
from main.forms import AddPost
from main.models import LikedBy, Following
from main.models import UserStats
from django.http import HttpResponse
from django.conf import settings
from validate.views import create_user_directory
import os

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

    return render(request, "main/page.html", {"username":name, "post":p, 'user_stats':s, 'user':us})


@login_required
def add_post(request):
    if request.method == "POST": # POST requests are encrypted, safer
        f = AddPost(request.POST, request.FILES) # enables the form for POST request
        print(request.POST, f.is_valid)
        print("valid")
        username = request.user.username
        a = request.POST.get("title")
        c = request.POST.get("content")
        user = User.objects.get(username=username)
        user_stats = UserStats.objects.get(user=user)
        d = request.FILES.get("image")
        create_user_directory(user=user, sub_directory='posts')

        print(user_stats.pfp, d)
        b = Post(user=user, title=a, contents=c, likes=0, user_pfp=user_stats.pfp, media_mp3=d) # makes the document's contents equall to what was inputed into the form.
        b.save()
        return HttpResponseRedirect("/page/")
    else:
        f = AddPost()
    return render(request, 'main/add_post.html', {"input_fields": f})

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
    return render(request, 'main/posts.html', {"post": post})

def edit_profile(request, name):
    username = request.user.username
    if name != username:
        return HttpResponseRedirect('/edit_error/')
    
    return render(request, 'main/edit_profile.html')

def edit_error(request):
    return render(request, 'main/unsafe_editing.html')