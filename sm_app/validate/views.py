from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import CreateNewUser
from main.models import UserStats
from django.contrib.auth.models import User
from main.models import Following, LikedBy, ArabaliConfigure, MessageNotificationSetting
import os
import shutil
from django.conf import settings
from django.contrib.auth.models import User
# creating a directory 

def create_user_directory(user, sub_directory):

        # Create a unique directory name based on the user's ID
        user_directory_name = f"{user.username}"

        # Construct the full path to the new directory
        new_directory_path = os.path.join(settings.MEDIA_ROOT, user_directory_name, sub_directory)

        # Create the new directory
        os.makedirs(new_directory_path, exist_ok=True)


def create_user_path_for_images(user, image, sub_directory):
    path = os.path.join(settings.MEDIA_ROOT, user.username, sub_directory, image)
    return path

# Create your views here.
def sign_up_page(request):
    if ArabaliConfigure.objects.get(name='Can Sign Up').allowed:
        if request.method == "POST":
                #print(request.FILES)  # Print uploaded files
                #print(request.POST.get('username'))
                #print(request.POST, request.POST.get('username'))
                name = request.POST.get('username')
                f = CreateNewUser(request.POST)
                if f.is_valid():
                    f.save()
                    # creating directory for the user
                    u = User.objects.get(username=name)
                    create_user_directory(user=u, sub_directory='profile')
                    us = UserStats(user=u, followers=0, pfp='Images/Default_User_Images/Default_Profile_Picture.png', banner='Images/Default_User_Images/Default_Banner_Image.png')
                    us.save()
                    b = Following(subscribers=u.username)
                    b.save()
                    c = LikedBy(name=u.username)
                    c.save()
                    return redirect('/login/')
        else:
            f = CreateNewUser()
        
        return render(request, "validate/sign-up.html", {"form": f})
    else:
        return render(request, 'main/error.html', {'issue': 'Signing up is disabled.'})


def login_page(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username, password)

    if user is not None:
        login(request, user)
        return redirect("main/page.html")
    return render(request, "validate/login.html")

def logout_page(request):
    logout(request)
    return render(request, "validate/logout.html")
