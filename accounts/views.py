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
        
        # 1. 'next' parameter gya jo modal form madhe add kela hota
        next_url = request.POST.get('next') 
        
        user = authenticate(username=u, password=p)
        
        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name + ' ' + user.last_name if user.first_name else u} !! 🤗✨")
            
            # 2. Redirect logic with Trigger Cleaning
            if next_url:
                # Jar URL madhe '?login_trigger=true' asel tar te kadhun taka
                # Jyamule page reload jhalya nantar popup parat yenar nahi
                clean_url = next_url.split('?')[0]
                return redirect(clean_url)
            
            return redirect(request.META.get('HTTP_REFERER', 'home'))
            
        else:
            messages.error(request, "Invalid username or password.")
            
    # POST nasel kinva login fail jhala tar parat maagchya page var pathva
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def logout_view(request):
    logout(request)
    messages.info(request, "Successfully logged out.")
    return redirect('home')


#---------------------------------------
# --- PROFILE UPDATE ---
#---------------------------------------

@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, "Profile updated successfully!",extra_tags='profile_msg')
    return redirect(request.META.get('HTTP_REFERER', '/'))

#---------------------------------------
# --- OTP SEND & VERIFY ---
#---------------------------------------
import json, random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import login

def send_otp(request):
    if request.method == 'POST':
        try:
            # 1. Data Handle (JSON kiva FormData)
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            email = data.get('email')
            username = data.get('username')

            if not email or not username:
                return JsonResponse({'status': 'error', 'message': 'Email and Username are required'}, status=400)
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({'status': 'error', 'message': 'Username already taken'}, status=400)
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({'status': 'error', 'message': 'Email already registered'}, status=400)

            otp = str(random.randint(100000, 999999))
            
            # 2. Session madhe Explicitly data save kara (Keys fix rahtat yane)
            request.session['registration_data'] = {
                'username': username,
                'email': email,
                'password': data.get('password'),
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', '')
            }
            request.session['email_otp'] = otp
            request.session.set_expiry(300) # 5 minutes

            # 3. Send Mail
            subject = "Verify your DevOpsVaultX Account"
            message = f"Hi {username},\n\nYour OTP for registration is: {otp}\nValid for 5 minutes."
            
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)
            
            return JsonResponse({'status': 'success', 'message': 'OTP sent to your email.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Server Error: {str(e)}'}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def verify_otp_and_register(request):
    if request.method == 'POST':
        try:
            user_otp = request.POST.get('otp')
            stored_otp = request.session.get('email_otp')
            reg_data = request.session.get('registration_data')

            if not stored_otp or user_otp != stored_otp:
                return JsonResponse({'status': 'error', 'message': 'Invalid or expired OTP'}, status=400)

            if not reg_data:
                return JsonResponse({'status': 'error', 'message': 'Registration session expired.'}, status=400)

            # --- USER CREATION ---
            # session madhun direct keys vapra jya aapan send_otp madhe set kelya hotya
            user = User.objects.create_user(
                username=reg_data['username'],
                email=reg_data['email'],
                password=reg_data['password'],
                first_name=reg_data.get('first_name', ''), 
                last_name=reg_data.get('last_name', '')
            )
            
            login(request, user)

            # Cleanup
            request.session.pop('email_otp', None)
            request.session.pop('registration_data', None)

            return JsonResponse({'status': 'success'})

        except Exception as e:
            print(f"ERROR: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f"DB Error: {str(e)}"}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)