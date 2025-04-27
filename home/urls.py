from django.urls import path
from home.views import home, contact, notification

urlpatterns = [
    path('home/', home, name='home'),
    path('contact/', contact, name='contact'),
    path('notification/', notification, name='notification')
]
