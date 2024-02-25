from validate import views as auth_v
from django.urls import path
urlpatterns = [
    path('sign-up/', auth_v.sign_up_page, name='sign-up')
]