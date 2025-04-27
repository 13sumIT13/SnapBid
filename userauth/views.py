from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from userauth.forms import SignUpForm, LoginForm
from django.contrib import messages

def home(request):
    return render(request, 'userauth/home.html')

def register(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)  # Instantiate the form with POST data
        if form.is_valid():
            form.save()  # Save the user
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')  # Redirect to the login page after successful registration
    else:
        form = SignUpForm()  # Instantiate an empty form for GET requests

    context = {'form': form}
    return render(request, 'userauth/register.html', context)


def user_login(request):

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password')
                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()

    context = {
        'form': form
    }
    
    
    return render(request, 'userauth/login.html' , context)



def user_logout(request):
    if request.method == 'POST':  # Log out only on POST to avoid accidental logouts via GET
        logout(request)
        return redirect('login')  # Redirect to login page after logout

    return render(request, 'registration/logout.html')  # Render a logout confirmation page