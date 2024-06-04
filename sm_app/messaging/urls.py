from django.urls import path, include
from messaging import views
urlpatterns = [
    path('chat/', views.chat_base, name='chat_base'),

    path('chat/<str:room>/<int:id>', views.chat_room_view, name='chat_room')
]