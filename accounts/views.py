import json
import random
import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMultiAlternatives
from dashboard.models import SystemLog
from django.db import IntegrityError

# Logger initialization to match your middleware audit logs
logger = logging.getLogger("request.audit")

# ==========================================
# 1. AUTHENTICATION (LOGIN/LOGOUT)
# ==========================================

def login_view(request):
    """ User login and redirect logic """
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        next_url = request.POST.get('next') 
        
        user = authenticate(username=u, password=p)
        
        if user:
            login(request, user)
            full_name = f"{user.first_name} {user.last_name}".strip()
            display_name = full_name if full_name else u
            # --- STEP 2: LOG ADDED ---
            SystemLog.objects.create(
                message=f"Access Granted: User @{u} logged into terminal",
                log_type="User"
            )
            # -------------------------
            messages.success(request, f"Welcome back, {display_name.title()}! 🤗✨")
            
            # Log successful login
            logger.info(f"User logged in: {u}")
            
            if next_url:
                clean_url = next_url.split('?')[0]
                return redirect(clean_url)
            
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            # --- STEP 2: FAILED LOG ---
            SystemLog.objects.create(
                message=f"Security Alert: Failed login attempt for @{u}",
                log_type="Error"
            )
            # -------------------------
            messages.error(request, "Invalid username or password.")
            # Log failed login attempt
            logger.warning(f"Failed login attempt for username: {u}")
            
    return redirect(request.META.get('HTTP_REFERER', '/'))

def logout_view(request):
    """ User logout """
    user_log = request.user.username if request.user.is_authenticated else "Anonymous"
    # --- STEP 2: LOG ADDED ---
    SystemLog.objects.create(
        message=f"Session Terminated: User @{user_log} logged out",
        log_type="User"
    )
    # -------------------------
    logout(request)
    logger.info(f"User logged out: {user_log}")
    messages.info(request, "Successfully logged out. See you soon!")
    return redirect('/')

# ==========================================
# 2. PROFILE MANAGEMENT
# ==========================================
@login_required
def update_profile(request):
    """ Handle user profile updates including password change """
    if request.method == 'POST':
        try:
            user = request.user
            old_username = user.username
            
            # Fetch data from POST request
            new_username = request.POST.get('username', user.username)
            new_email = request.POST.get('email', user.email)
            
            # 1. USERNAME/EMAIL UNIQUE CHECK
            # Prevent update if the new username is already taken by another user
            if User.objects.exclude(pk=user.pk).filter(username=new_username).exists():
                messages.error(request, "This username is already taken.")
                return redirect(request.META.get('HTTP_REFERER', '/'))

            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.username = new_username
            user.email = new_email
            
            new_pass = request.POST.get('new_password')
            
            # 2. PASSWORD UPDATE LOGIC
            if new_pass and len(new_pass.strip()) > 0:
                user.set_password(new_pass)
                user.save()
                # Update session to prevent logout after password change
                update_session_auth_hash(request, user)
            else:
                user.save()
                
            # Logging and System Audit
            logger.info(f"Profile updated for user: {old_username}")
            SystemLog.objects.create(
                message=f"Profile Updated: Profile modified for @{old_username}",
                log_type="User"
            )
            
            messages.success(request, "Profile updated successfully!")
            
        except IntegrityError:
            messages.error(request, "Username or Email already exists.")
        except Exception as e:
            logger.error(f"Profile update failed for {request.user.username}: {str(e)}")
            messages.error(request, "A technical error occurred.")
    
    return redirect(request.META.get('HTTP_REFERER', '/'))

# ==========================================
# 3. REGISTRATION WITH OTP (AJAX)
# ==========================================

def send_otp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
            email = data.get('email')
            username = data.get('username')
            password = data.get('password')
            f_name = data.get('first_name', '') 
            l_name = data.get('last_name', '')

            if not email or not username or not password:
                return JsonResponse({'status': 'error', 'message': 'All fields are required'}, status=400)
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({'status': 'error', 'message': 'Username already taken'}, status=400)
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({'status': 'error', 'message': 'Email already registered'}, status=400)

            otp = str(random.randint(100000, 999999))
            
            # Storing registration data in session
            request.session['registration_data'] = {
                'username': username,
                'email': email,
                'password': make_password(password), 
                'first_name': f_name,
                'last_name': l_name
            }
            request.session['email_otp'] = otp
            request.session.set_expiry(300) # 5 minutes expiry

            subject = "IDENTITY VERIFICATION FOR DEVOPSVAULTX ACCOUNT 🛡️"
            text_content = f"Your OTP is: {otp}"

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ margin: 0; padding: 0; background-color: #f8fafc; }}
                    .email-wrapper {{ width: 100%; padding: 40px 0; }}
                    .email-container {{ 
                        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                        max-width: 550px; 
                        margin: 0 auto; 
                        background-color: #ffffff; 
                        border: 1px solid #e2e8f0; 
                        border-radius: 16px; 
                        overflow: hidden; 
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
                    }}
                    .header {{ background: #0f172a; padding: 40px 20px; text-align: center; }}
                    .logo {{ color: #ffffff; font-size: 26px; font-weight: 800; letter-spacing: -0.5px; text-transform: uppercase; }}
                    .logo span {{ color: #ff4500; }}
                    .body {{ padding: 45px 35px; text-align: center; color: #1e293b; }}
                    h2 {{ font-size: 20px; font-weight: 700; margin-bottom: 20px; color: #0f172a; letter-spacing: 0.5px; }}
                    .otp-box {{ background-color: #f1f5f9; border-radius: 12px; padding: 25px; margin: 30px 0; font-size: 36px; font-weight: 800; letter-spacing: 12px; color: #0f172a; border: 1px solid #cbd5e1; }}
                    .security-notice {{ font-size: 12px; color: #94a3b8; margin-top: 25px; padding: 15px; background-color: #f8fafc; border-radius: 8px; }}
                    .footer {{ background-color: #ffffff; padding: 30px 20px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #f1f5f9; }}
                    .tagline {{ font-weight: 700; color: #0f172a; margin-bottom: 5px; }}
                </style>
            </head>
            <body>
                <div class="email-wrapper">
                    <div class="email-container">
                        <div class="header"><div class="logo">DevOps<span>VaultX</span></div></div>
                        <div class="body">
                            <h2>IDENTITY VERIFICATION REQUIRED</h2>
                            <div class="otp-box">{otp}</div>
                            <div class="security-notice">
                                This One-Time Password (OTP) is valid for <strong>5 minutes</strong>.<br>
                                Never share this code or forward this communication to any third party.
                            </div>
                        </div>
                        <div class="footer">
                            <div class="tagline">SECURE. AUTOMATE. SCALE.</div>
                            &copy; 2026 DEVOPSVAULTX. ALL RIGHTS RESERVED.
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            # Log successful OTP generation
            logger.info(f"OTP generated and sent to: {email}")
            
            return JsonResponse({'status': 'success', 'message': 'OTP Sent Successfully!'})
            
        except Exception as e:
            # Log the full exception for debugging
            logger.error(f"OTP Send Error for {email if 'email' in locals() else 'unknown'}: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Something Went Wrong.'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid Request'}, status=400)

def verify_otp_and_register(request):
    """ Verify OTP and complete user registration """
    if request.method == 'POST':
        try:
            user_otp = request.POST.get('otp')
            stored_otp = request.session.get('email_otp')
            reg_data = request.session.get('registration_data')

            # 1. Validate OTP
            if not stored_otp or user_otp != stored_otp:
                logger.warning(f"Invalid OTP attempt for email: {reg_data.get('email') if reg_data else 'Unknown'}")
                return JsonResponse({'status': 'error', 'message': 'Invalid or Expired OTP'}, status=400)

            # 2. Check if session data exists
            if not reg_data:
                return JsonResponse({'status': 'error', 'message': 'Session Expired. Please Try Again.'}, status=400)

            # 3. Final check for existing username
            if User.objects.filter(username=reg_data['username']).exists():
                return JsonResponse({'status': 'error', 'message': 'Username Already Taken'}, status=400)

            # 4. Create and save user correctly
            user = User(
                username=reg_data['username'],
                email=reg_data['email'],
                first_name=reg_data.get('first_name', ''),
                last_name=reg_data.get('last_name', '')
            )
            # Assign the already hashed password from session
            user.password = reg_data['password'] 
            user.save()
            
            # 5. Log the user in
            login(request, user)
            
            # --- SYSTEM AUDIT LOG ---
            SystemLog.objects.create(
                message=f"New Profile Initialized: User @{user.username} joined DevOpsVaultX",
                log_type="User"
            )
            # ------------------------

            logger.info(f"New user registered and verified: {user.username}")
            messages.success(request, f"Welcome to DevOpsVaultX, {user.username}! 🛡️🚀")

            # 6. Cleanup session data
            request.session.pop('email_otp', None)
            request.session.pop('registration_data', None)

            return JsonResponse({'status': 'success'})

        except Exception as e:
            logger.error(f"Account creation failed: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Account Creation Failed.'}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid Request'}, status=400)