from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import createNewUser
# Create your views here.
def sign_up_page(request):
    if request.method == "POST":
        print(request.POST)
        f = createNewUser(request.POST)
        if f.is_valid():
            f.save()
            return redirect('/page/')
    else:
        f = createNewUser()
    
    return render(request, "validate/sign-up.html", {"form": f})

def login_page(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username, password)

    if user is not None:
        login(request, user)
        return redirect("main/page.html")
    return render(request, "validate/login.html")

def logout_page(request):
    return render(request, "validate/logout.html")