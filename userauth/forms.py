from django import forms
from userauth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = {'username', 'first_name', 'last_name', 'email'}

    
class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=50)