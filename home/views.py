from django.shortcuts import render
from django.contrib import messages
from product.models import Notification

# Create your views here.

def home(request):
    return render(request, 'home/home.html')

def contact(request):
    return render(request, 'home/contact.html')

def notification(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'home/notification.html', {'notifications': notifications})