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
        
        html_content = f"<html><body><h2>📬 New Message: {name}</h2><p>{message_text}</p></body></html>"
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