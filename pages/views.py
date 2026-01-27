from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import now
from datetime import timedelta
from products.models import Product
from .models import ContactMessage



def home(request):
    featured_products = Product.objects.filter(is_new=True)
    return render(request, 'pages/home.html', {'products': featured_products})


def about(request):
    return render(request, 'pages/about.html')


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()
        ip = get_client_ip(request)

        # Rate limit: 1 message / minute
        one_min_ago = now() - timedelta(minutes=1)
        if ContactMessage.objects.filter(ip_address=ip, created_at__gte=one_min_ago).exists():
            messages.error(request, "⏳ Please wait before sending another message.")
            return redirect("contact")

        if not name or not email or not message:
            messages.error(request, "⚠️ All fields are required.")
            return redirect("contact")

        # Save to DB
        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message,
            ip_address=ip
        )

        from django.core.mail import EmailMultiAlternatives

    # HTML content with emojis and modern card style
        html_content = f"""
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; background:#f4f4f4; padding:20px;">
            <div style="max-width:600px; margin:auto; background:#fff; border-radius:12px; box-shadow:0 4px 20px rgba(0,0,0,0.1); overflow:hidden;">
            
            <!-- Header -->
            <div style="background:#4CAF50; color:#fff; padding:20px; text-align:center;">
                <h1 style="margin:0; font-size:24px;">📬 New Contact Message</h1>
            </div>

            <!-- Body -->
            <div style="padding:20px; color:#333; line-height:1.5;">
                <p>👤 <strong>Name:</strong> {name}</p>
                <p>📧 <strong>Email:</strong> {email}</p>
                <p>💬 <strong>Message:</strong><br>{message}</p>

                <!-- Optional button -->
                <p style="text-align:center; margin-top:30px;">
                <a href="mailto:{email}" style="text-decoration:none; background:#4CAF50; color:#fff; padding:12px 25px; border-radius:8px; font-weight:bold;">Reply to {name}</a>
                </p>
            </div>

            <!-- Footer -->
            <div style="background:#f7f7f7; color:#999; text-align:center; font-size:12px; padding:15px;">
                This message was sent from DevOpsVaultX website contact form.
            </div>
            </div>
        </body>
        </html>
        """

        # Send email
        email = EmailMultiAlternatives(
            subject=settings.CONTACT_EMAIL_SUBJECT,
            body=f"Name: {name}\nEmail: {email}\nMessage:\n{message}",  # plain text fallback
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_RECEIVER_EMAIL],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        messages.success(request, "✅ Message sent successfully!")
        return redirect("contact")


    return render(request, "pages/contact.html")
