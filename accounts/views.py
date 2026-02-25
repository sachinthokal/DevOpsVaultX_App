from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        u, p = request.POST.get('username'), request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            messages.success(request, f"Welcome {u}!")
        else:
            messages.error(request, "Invalid credentials")
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def register_view(request):
    if request.method == 'POST':
        u, e, p = request.POST.get('username'), request.POST.get('email'), request.POST.get('password')
        if User.objects.filter(username=u).exists():
            messages.error(request, "Username taken")
        else:
            user = User.objects.create_user(username=u, email=e, password=p)
            login(request, user)
            messages.success(request, "Account Created!")
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def logout_view(request):
    logout(request)
    messages.info(request, "Logged out.")
    return redirect('home')