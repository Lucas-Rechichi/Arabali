from django.shortcuts import render, HttpResponseRedirect
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from validate.forms import User
from django.contrib.auth.decorators import login_required
from main.models import Post
from main.forms import AddPost, EditProfile
from main.models import LikedBy, Following
from main.models import UserStats
from django.http import HttpResponse
from django.conf import settings
from validate.views import create_user_directory
import os
from main.errors import UsernameError

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
        b = Post(user=user, title=a, contents=c, likes=0, media_mp3=d)
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

    # checking that the right user is acessing this page.
    username = request.user.username
    if name != username:
        return render(request, 'main/error.html', {'issue': 'Cannot access this users profile'})
    
    # setup: geting useful databace objects.
    user = User.objects.get(username=username)
    old_username = user.username
    user_stats = UserStats.objects.get(user=user)
    user_liked_by = LikedBy.objects.get(name=username)
    user_following = Following.objects.get(subscribers=username)
    users = User.objects.all()
    print(users)

    # form init
    if request.method == 'POST':
        f = EditProfile(request.POST, request.FILES)
        initial_values = {
        'username': user.username,
        }

        # Username change
        if request.POST.get('username') != initial_values['username']: # if the user has changed their username
            print('Username is being changed')
            # Checks
            if request.POST.get('username') == 'Images': # if the new username is Images
                error = 'Cannot be named Images due to the default image directory being called Images.'
                print(f'error: {error}')
                return render(request, 'main/error.html', {'issue': error})
            for x in range(0, users.count()):
                if request.POST.get('username') == str(users[x]): # if the new usermane is any existing username on the app
                    error = 'Username Taken.'
                    print(f'error: {error}')
                    return render(request, 'main/error.html', {'issue': error})
                
            # Changes username and important models that rely on the name being the username.
            new_username = request.POST.get('username')
            user_liked_by.name = new_username
            user_liked_by.save()
            print('Likedby Changed Sucessfully')
            user_following.subscribers = new_username
            user_following.save()
            print('Following Changed Sucessfully')

            # define the changing of the username's directory (for neatness of code)
            def change_user_directory(old_dir, new_dir):
                os.replace(old_dir, new_dir)
            
            # Changing directories
            old_dir = os.path.join('arabali_users', old_username)
            new_dir = os.path.join('arabali_users', new_username)
            print('Directory Updated Sucessfully')
            print(f'New name: {new_username}')

        else:
            new_username = username
            print('Username remains the same')

            old_dir = os.path.join('arabali_users', old_username)
            new_dir = os.path.join('arabali_users', new_username)
            
        
            def change_user_directory(old_dir, new_dir):
                os.replace(old_dir, new_dir)
            print(f'Current name: {new_username}')

        

        # Saving relevant information from the old user_stats
        followers_instance = user_stats.followers # now the new username is used.
        following_instance = list(user_stats.following.all())

        # function that unpacks followers and adds nthem to the following of a userstats object.
        def adding_following_to_userstats(user_stats, following_instance):
            for follower in following_instance:
                user_stats.following.add(follower)
            user_stats.save()

        if request.FILES.get('profile_picture') and request.FILES.get('profile_banner'): # both changed
            print('New pfp and banner')

            print('-------------')

            # old file paths for old images
            raw_old_pfp_path = user_stats.pfp.url
            raw_old_banner_path = user_stats.banner.url
            old_pfp_path = raw_old_pfp_path.removeprefix('/')
            old_banner_path = raw_old_banner_path.removeprefix('/')
            print(f'Old pfp path: {old_pfp_path} \nOld banner path: {old_banner_path}')

            print('-------------')

            # new paths for new images
            new_pfp = request.FILES.get('profile_picture')
            new_banner = request.FILES.get('profile_banner')
            print(f'New pfp: {new_pfp} \nNew banner: {new_banner}')

            # delete old image paths
            os.remove(old_pfp_path)
            print(f'Deleted file at {old_pfp_path}')

            print('-------------')

            os.remove(old_banner_path)
            print(f'Deleted file at {old_banner_path}')


            # happends after the images are deleted, 
            # otherwise OS cannot find the images so that they can be deleted.
            change_user_directory(old_dir, new_dir)
            print('Directory Updated Sucessfully')       
            
        elif request.FILES.get('profile_picture'): # only pfp changed
            print('New pfp, old banner')

            print('-------------')

            # old file paths for old images.
            raw_old_pfp_path = user_stats.pfp.url
            raw_old_banner_path = user_stats.banner.url
            old_pfp_path = raw_old_pfp_path.removeprefix('/')
            old_banner_path = raw_old_banner_path.removeprefix('/')
            print(f'Old pfp path: {old_pfp_path} \nOld banner path: {old_banner_path}')

            # preparing old image for resubmission to userstats.
            raw_banner_path = user_stats.banner
            raw_banner_path_string = str(raw_banner_path)
            modified_old_banner = raw_banner_path_string.replace(old_username, new_username)
            new_banner = modified_old_banner

            # getting new image. 
            new_pfp = request.FILES.get('profile_picture')

            print(f'New pfp: {new_pfp} \nCurrent banner (path modified): {new_banner}')

            print('-------------')

            # delete old image paths
            os.remove(old_pfp_path)
            print(f'Deleted file at {old_pfp_path}')

            # happends after the images are deleted, 
            # otherwise OS cannot find the images so that they can be deleted.
            change_user_directory(old_dir, new_dir)
            print('Directory Updated Sucessfully')

        elif request.FILES.get('profile_banner'): # only banner changed
            print('Old pfp, new banner')

            print('-------------')

            # old file paths for old images.
            raw_old_pfp_path = user_stats.pfp.url
            raw_old_banner_path = user_stats.banner.url
            old_pfp_path = raw_old_pfp_path.removeprefix('/')
            old_banner_path = raw_old_banner_path.removeprefix('/')
            print(f'Old pfp path: {old_pfp_path} \nOld banner path: {old_banner_path}')

            # preparing old image for resubmission to userstats.
            raw_pfp_path = user_stats.pfp
            raw_pfp_path_string = str(raw_pfp_path)
            modified_old_pfp = raw_pfp_path_string.replace(old_username, new_username)
            new_pfp = modified_old_pfp

            # getting new image. 
            new_banner = request.FILES.get('profile_banner')

            print(f'Current pfp (path modified): {new_pfp} \nNew banner: {new_banner}')

            print('-------------')

            # delete old image paths
            os.remove(old_banner_path)
            print(f'Deleted file at {old_banner_path}')

            # happends after the images are deleted, 
            # otherwise OS cannot find the images so that they can be deleted.
            change_user_directory(old_dir, new_dir)
            print('Directory Updated Sucessfully')

        else: # neither changed
            print('Old pfp and banner')

            # old file paths for old images
            raw_old_pfp_path = user_stats.pfp.url
            raw_old_banner_path = user_stats.banner.url
            old_pfp_path = raw_old_pfp_path.removeprefix('/')
            old_banner_path = raw_old_banner_path.removeprefix('/')
            print(f'Old pfp path: {old_pfp_path} \nOld banner path: {old_banner_path}')

            # preparing old images for resubmission to userstats.
            raw_banner_path = user_stats.banner
            raw_banner_path_string = str(raw_banner_path)
            modified_old_banner = raw_banner_path_string.replace(old_username, new_username)
            new_banner = modified_old_banner
            raw_pfp_path = user_stats.pfp
            raw_pfp_path_string = str(raw_pfp_path)
            modified_old_pfp = raw_pfp_path_string.replace(old_username, new_username)
            new_pfp = modified_old_pfp
            print(f'Current pfp (path modified): {new_pfp} \nCurrent banner (path modified): {new_banner}')

            # happends after the images are deleted, 
            # otherwise OS cannot find the images so that they can be deleted.
            change_user_directory(old_dir, new_dir)
            print('Directory Updated Sucessfully')

        # deletion of old userstats
        user_stats.delete()
        
        # create new userstats, modify username here due to issues with image directories
        new_user = User.objects.get(username=old_username)
        new_user.username = new_username
        new_user.save()
        new_user_stats = UserStats(user=new_user, followers=followers_instance, pfp=new_pfp, banner=new_banner)
        new_user_stats.save()
        
        print('Username Changed Sucessfully')
        
        # preparing data for new userstats
        adding_following_to_userstats(user_stats=new_user_stats, following_instance=following_instance)
        new_user_stats.save()
        
        return HttpResponseRedirect(f'/profile/{new_username}')
   
    else:
        initial_values = {
        'username': user.username,
    }
    f = EditProfile(initial=initial_values)        
    return render(request, 'main/edit_profile.html', {'form': f, 'user_stats': user_stats})

def error(request, error):
    return render(request, 'main/error.html', {'error':error})
    