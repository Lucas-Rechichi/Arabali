from validate import views as valid_v
from django.urls import path
urlpatterns = [
    path('sign-up/', valid_v.sign_up_page, name='sign-up'),
    path('logout/', valid_v.logout_page, name='logout'),
]