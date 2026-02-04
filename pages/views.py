from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.timezone import now
from datetime import timedelta
from products.models import Product
from .models import ContactMessage
import logging

# Logger client
# DevOps Tip: Using __name__ helps identify exactly where the log was generated.
logger = logging.getLogger(__name__)

# ======================
# Get Client IP (Helper)
# ======================
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

# ======================
# Home Page
# ======================
def home(request):
    ip = get_client_ip(request)
    try:
        featured_products = Product.objects.filter(is_new=True)
        # Added 'extra' to ensure IP is captured as a separate field in JSON logs
        logger.info(f"Home page requested", extra={'ip': ip})
        return render(request, 'pages/home.html', {'products': featured_products})
    except Exception as e:
        logger.error(f"Error loading home page for IP {ip}: {str(e)}", exc_info=True, extra={'ip': ip})
        return render(request, 'pages/home.html', {'products': []})

# ======================
# About Page
# ======================
def about(request):
    ip = get_client_ip(request)
    # Correctly passing IP to the JSON formatter
    logger.info("About page requested", extra={'ip': ip})
    return render(request, 'pages/about.html')

# ======================
# Buy / Payment Simulation
# ======================
def buy_product(request, product_id):
    ip = get_client_ip(request)
    # Simulation: If you use 'failure@razorpay', we log it as 402
    # In a real scenario, this check would happen after Razorpay callback
    payment_failed = True # Only for testing failure logs

    if payment_failed:
        # Using status 402 (Payment Required) to differentiate from 200 (OK)
        logger.error(f"Payment Failed for product {product_id}", extra={'ip': ip, 'status_code': 402})
        return render(request, 'pages/payment_failed.html', status=402)
    
    logger.info(f"Payment Successful for product {product_id}", extra={'ip': ip, 'status_code': 200})
    return redirect('home')

# ======================
# Contact Page / Form
# ======================
def contact(request):
    ip = get_client_ip(request)
    logger.info("Contact page requested", extra={'ip': ip})

    # Default empty context for rendering
    context = {}

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message_text = request.POST.get("message", "").strip()

        # Rate limit: 1 message / minute
        one_min_ago = now() - timedelta(minutes=1)
        if ContactMessage.objects.filter(ip_address=ip, created_at__gte=one_min_ago).exists():
            logger.warning(f"Rate limit exceeded! IP: {ip}", extra={'ip': ip})
            messages.error(request, "⏳ Please wait before sending another message.")
            context.update({'name': name, 'email': email, 'message': message_text})
            return render(request, "pages/contact.html", context)  # 200 OK

        # Validate fields
        if not name or not email or not message_text:
            logger.warning(f"Validation Failed: Incomplete form", extra={'ip': ip})
            messages.error(request, "⚠️ All fields are required.")
            context.update({'name': name, 'email': email, 'message': message_text})
            return render(request, "pages/contact.html", context)  # 200 OK

        try:
            # Save to database
            ContactMessage.objects.create(
                name=name, email=email, message=message_text, ip_address=ip
            )
            logger.info(f"SUCCESS: Contact message saved from {email}", extra={'ip': ip})

            # Send email
            html_content = f"<html><body><h2>📬 New Message: {name}</h2><p>{message_text}</p></body></html>"
            email_msg = EmailMultiAlternatives(
                subject=settings.CONTACT_EMAIL_SUBJECT,
                body=message_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.CONTACT_RECEIVER_EMAIL],
            )
            email_msg.attach_alternative(html_content, "text/html")
            email_msg.send()
            logger.info(f"SUCCESS: Email sent for user {email}", extra={'ip': ip})

            messages.success(request, "✅ Message sent successfully!")
            # Clear form fields after successful submission
            context.update({'name': '', 'email': '', 'message': ''})
            return render(request, "pages/contact.html", context)  # 200 OK

        except Exception as e:
            logger.error(f"CRITICAL: Form processing failed", exc_info=True, extra={'ip': ip})
            messages.error(request, "❌ Something went wrong.")
            context.update({'name': name, 'email': email, 'message': message_text})
            return render(request, "pages/contact.html", context)  # 200 OK

    # GET request
    return render(request, "pages/contact.html", {'name': '', 'email': '', 'message': ''})