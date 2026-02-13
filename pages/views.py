from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.timezone import now
from datetime import timedelta
from products.models import Product
from .models import ContactMessage
import time

# ======================
# Home Page
# ======================
def home(request):
    # Middleware automatic IP ani status log karel
    featured_products = Product.objects.filter(is_new=True)
    return render(request, 'pages/home.html', {'products': featured_products})

# ======================
# About Page
# ======================
def about(request):
    return render(request, 'pages/about.html')

# ======================
# Contact Page / Form
# ======================
def contact(request):
    context = {'name': '', 'email': '', 'message': ''}

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message_text = request.POST.get("message", "").strip()
        
        # Real IP middleware kadun automatic jail, ithe garaj nahi
        ip = request.META.get("REMOTE_ADDR") 

        # Rate limit: 1 message / minute
        one_min_ago = now() - timedelta(minutes=1)
        if ContactMessage.objects.filter(ip_address=ip, created_at__gte=one_min_ago).exists():
            messages.error(request, "⏳ Please wait before sending another message.")
            context.update({'name': name, 'email': email, 'message': message_text})
            return render(request, "pages/contact.html", context)

        # Validate fields
        if not name or not email or not message_text:
            messages.error(request, "⚠️ All fields are required.")
            context.update({'name': name, 'email': email, 'message': message_text})
            return render(request, "pages/contact.html", context)

        # Save & Send Email (Central middleware will log if this fails)
        ContactMessage.objects.create(
            name=name, email=email, message=message_text, ip_address=ip
        )
        
        # html_content = f"<html><body><h2>📬 New Message: {name}</h2><p>{message_text}</p></body></html>"
        html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8">
            <title>New Contact Message</title>
            </head>

            <body style="margin:0;padding:0;background-color:#f2f5f9;font-family:Arial,Helvetica,sans-serif;">

            <table width="100%" cellpadding="0" cellspacing="0" style="padding:30px 0;">
            <tr>
            <td align="center">

            <table width="600" cellpadding="0" cellspacing="0" 
            style="background:#ffffff;border-radius:12px;overflow:hidden;
            box-shadow:0 10px 25px rgba(0,0,0,0.08);">

            <!-- HEADER -->
            <tr>
            <td align="center" 
            style="background:linear-gradient(90deg,#0d6efd,#0a58ca);
            padding:30px;color:#ffffff;">

            <img src="https://devopsvaultx.com/static/images/Email_logo.png" 
            alt="DevOpsVaultX Logo" 
            style="max-height:60px;margin-bottom:15px;display:block;" />

            <h2 style="margin:0;font-size:22px;">📬 New Contact Message</h2>
            <p style="margin:5px 0 0 0;font-size:14px;opacity:0.9;">
            🚀 DevOpsVaultX Contact Notification
            </p>

            </td>
            </tr>

            <!-- CONTENT -->
            <tr>
            <td style="padding:30px;color:#333;font-size:15px;line-height:1.6;">

            <p><strong>👤 Name:</strong> {name}</p>
            <p><strong>📧 Email:</strong> {email}</p>

            <p style="margin-top:25px;"><strong>💬 Message:</strong></p>

            <div style="
            background:#f8fafc;
            border-left:5px solid #0d6efd;
            padding:18px;
            border-radius:8px;
            margin-top:10px;
            font-style:italic;
            color:#444;">
            {message_text}
            </div>

            </td>
            </tr>

            <!-- FOOTER -->
            <tr>
            <td align="center"
            style="background:#f9fafb;
            padding:20px;
            font-size:13px;
            color:#777;">

            🔔 This email was generated automatically<br>
            🌐 <a href="https://devopsvaultx.com" 
            style="color:#0d6efd;text-decoration:none;">
            devopsvaultx.com
            </a>

            </td>
            </tr>

            </table>

            </td>
            </tr>
            </table>

            </body>
            </html>
            """
        email_msg = EmailMultiAlternatives(
            subject=settings.CONTACT_EMAIL_SUBJECT,
            body=message_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_RECEIVER_EMAIL],
        )
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send()

        messages.success(request, "✅ Message sent successfully!")
        return render(request, "pages/contact.html", {'name': '', 'email': '', 'message': ''})

    return render(request, "pages/contact.html", context)