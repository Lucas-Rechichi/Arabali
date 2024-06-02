from django.shortcuts import render

# Create your views here.
def chat_base(request):
    return render(request, 'messaging/chat_base.html')