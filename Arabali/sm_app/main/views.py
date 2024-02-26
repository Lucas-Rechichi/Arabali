from django.shortcuts import render
from validate.forms import User

# Create your views here.
def home(request):
    return render(request, "main/home.html")

def page(request):
    username = request.user.username
    u = User.objects.get(username=username)
    name = u.get_username()
    return render(request, "main/page.html", {"user":name})