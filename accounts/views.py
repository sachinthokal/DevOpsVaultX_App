import json
import random
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings

# --- LOGIN & LOGOUT ---

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name if user.first_name else u}!")
        else:
            messages.error(request, "Invalid username or password.")
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def logout_view(request):
    logout(request)
    messages.info(request, "Successfully logged out.")
    return redirect('home')

# --- PROFILE UPDATE ---

@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, "Profile updated successfully!")
    return redirect(request.META.get('HTTP_REFERER', '/'))

# --- REGISTRATION WITH OTP ---

def send_otp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            username = data.get('username')

            if not email or not username:
                return JsonResponse({'status': 'error', 'message': 'Email and Username are required'}, status=400)
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({'status': 'error', 'message': 'Username already taken'}, status=400)

            otp = str(random.randint(100000, 999999))
            
            # Session storage
            request.session['registration_data'] = data
            request.session['email_otp'] = otp
            request.session.set_expiry(300) 

            # Send Mail
            subject = "Verify your DevOpsVaultX Account"
            message = f"Hi {username},\n\nYour OTP for registration is: {otp}\nValid for 5 minutes."
            
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)
            
            return JsonResponse({'status': 'success', 'message': 'OTP sent to your email.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Check SMTP settings.'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def verify_otp_and_register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_otp = data.get('otp')
            stored_otp = request.session.get('email_otp')
            reg_data = request.session.get('registration_data')

            if not stored_otp or user_otp != stored_otp:
                return JsonResponse({'status': 'error', 'message': 'Invalid or expired OTP'}, status=400)

            # User Creation
            user = User.objects.create_user(
                username=reg_data['username'],
                email=reg_data['email'],
                password=reg_data['password'],
                first_name=reg_data.get('first_name', ''),
                last_name=reg_data.get('last_name', '')
            )
            user.save()
            
            login(request, user)
            
            del request.session['email_otp']
            del request.session['registration_data']
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)