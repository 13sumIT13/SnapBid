from django.shortcuts import render
from django.contrib import messages

# Create your views here.

def home(request):
    return render(request, 'home/home.html')

def contact(request):
    return render(request, 'home/contact.html')

