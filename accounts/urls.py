from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # --- Authentication ---
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # --- Profile Management ---
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # --- Registration & OTP ---
    path('send-otp/', views.send_otp, name='send_otp'),
    path('register/', views.verify_otp_and_register, name='register'), 
    
    # --- Password Reset Flow ---
    
    # 1. User enters email to reset password
    path('password-reset/', 
     auth_views.PasswordResetView.as_view(
         template_name='accounts/password_reset.html',
         # ही ओळ खूप महत्त्वाची आहे, यामुळे डिफॉल्ट venv फाईल स्किप होईल:
         email_template_name='accounts/password_reset_email.html', 
         html_email_template_name='accounts/password_reset_email.html',
         subject_template_name='accounts/password_reset_subject.txt',
         success_url=reverse_lazy('accounts:password_reset_done'),
         extra_email_context={'app_name': 'accounts'}
     ), 
     name='password_reset'),
    
    # 2. Page shown after email is sent
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    # 3. The link user clicks in their email
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url=reverse_lazy('accounts:password_reset_complete')
         ), 
         name='password_reset_confirm'),
    
    # 4. Final page showing password reset was successful
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]