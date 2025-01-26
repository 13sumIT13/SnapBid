from django.urls import path
from userauth.views import user_login, register

urlpatterns = [

    path('register/', register, name='register'),
]
