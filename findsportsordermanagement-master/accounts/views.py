from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import logout as django_logout
from django.contrib.auth import authenticate, login

from django.contrib import messages

# Create your views here.
def index(request):

    return render(request, 'login/login.html',{})

def login(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("pass")

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            messages.info(request, "Invalid Credentials! Please contact admin if forgot password .")

    return render(request, 'login/login.html', {})

@login_required
def logout(request):
    django_logout(request)
    return redirect("/login")
