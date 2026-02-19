import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.timezone import now, localtime
from datetime import timedelta
from products.models import Product
from .models import ContactMessage

# Middleware logger sobat sync karnyasaathi "request.audit" naav vapra
logger = logging.getLogger("request.audit")
ist_now = localtime(now()).strftime('%d-%m-%Y %H:%M:%S')

# ======================
# Home Page
# ======================
def home(request):
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
        ip = request.META.get("REMOTE_ADDR") 

        # 1. Rate limit: 1 message per minute
        one_min_ago = now() - timedelta(minutes=1)
        if ContactMessage.objects.filter(ip_address=ip, created_at__gte=one_min_ago).exists():
            messages.error(request, "⏳ Please wait before sending another message.")
            return render(request, "pages/contact.html", {'name': name, 'email': email, 'message': message_text})

        # 2. Validation
        if not name or not email or not message_text:
            messages.error(request, "⚠️ All fields are required.")
            return render(request, "pages/contact.html", {'name': name, 'email': email, 'message': message_text})

        # 3. Save to Database
        ContactMessage.objects.create(name=name, email=email, message=message_text, ip_address=ip)
        
        # 4. Modern Dark Email Template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin:0; padding:0; background-color:#0f172a; font-family: 'Segoe UI', sans-serif;">
            <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #0f172a; padding: 40px 0;">
                <tr>
                    <td align="center">
                        <table width="700" border="0" cellspacing="0" cellpadding="0" style="background:#1e293b; border-radius:20px; overflow:hidden; box-shadow:0 25px 50px -12px rgba(0,0,0,0.5); border: 1px solid #334155;">
                            <tr><td height="6" style="background:linear-gradient(90deg, #3b82f6, #06b6d4, #3b82f6);"></td></tr>
                            <tr>
                                <td align="center" style="padding:45px 30px; background-color:#1e293b;">
                                    <img src="https://devopsvaultx.com/static/images/Email_logo.png" alt="DevOpsVaultX" style="max-height:55px; margin-bottom:20px; display:block;" />
                                    <h2 style="color:#f8fafc; margin:0; font-size:26px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase;">DevOps<span style="color:#ef4444;">VaultX</span></h2>
                                    <p style="color:#64748b; margin:10px 0 0 0; font-size:13px; font-weight:600; text-transform:uppercase; letter-spacing:3px;">Inbound Signal Log: {ist_now} IST</p>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding:0 60px 50px 60px;">
                                    <div style="background:#0f172a; border-radius:15px; border:1px solid #334155; padding:35px;">
                                        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom:30px;">
                                            <tr>
                                                <td width="50%" style="padding-bottom: 20px;">
                                                    <p style="margin:0; font-size:11px; color:#475569; text-transform:uppercase; font-weight:800; letter-spacing:1px;">👤 USER</p>
                                                    <p style="margin:6px 0 0 0; font-size:16px; color:#f1f5f9; font-weight:600;">{name}</p>
                                                </td>
                                                <td width="50%" style="padding-bottom: 20px;">
                                                    <p style="margin:0; font-size:11px; color:#475569; text-transform:uppercase; font-weight:800; letter-spacing:1px;">📧 EMAIL</p>
                                                    <p style="margin:6px 0 0 0; font-size:16px; color:#3b82f6; font-weight:600;"><a href="mailto:{email}" style="color:#3b82f6; text-decoration:none;">{email}</a></p>
                                                </td>
                                            </tr>
                                        </table>
                                        <p style="margin:0; font-size:11px; color:#475569; text-transform:uppercase; font-weight:800; letter-spacing:1px; margin-bottom:12px;">📄 Message</p>
                                        <div style="background:#1a202c; color:#cbd5e1; font-family: 'Courier New', monospace; font-size:14px; line-height:1.8; border-left: 4px solid #3b82f6; padding: 20px; border-radius: 8px;">
                                            {message_text}
                                        </div>
                                    </div>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding:0 60px 45px 60px;">
                                    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="border-top:1px solid #334155; padding-top:25px;">
                                        <tr>
                                            <td>
                                                <p style="margin:0; font-size:11px; color:#64748b; font-weight:600;">Node Status: <span style="color:#22c55e;">● ACTIVE</span></p>
                                                <p style="margin:4px 0 0 0; font-size:11px; color:#475569;">IP: {ip} | Protocol: HTTPS/TLS</p>
                                            </td>
                                            <td align="right">
                                                <a href="https://devopsvaultx.com" style="background:linear-gradient(135deg, #3b82f6, #2563eb); color:#ffffff; padding:12px 24px; text-decoration:none; border-radius:10px; font-weight:bold; font-size:13px; display:inline-block;">Access Terminal</a>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                        <p style="margin:30px 0 0 0; font-size:11px; color:#475569; text-align:center;">&copy; 2026 DEVOPSVAULTX INFRASTRUCTURE</p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        # 5. Email Dispatch with Logging
        try:
            email_msg = EmailMultiAlternatives(
                subject=f"DevOpsVaultX - New Message from {name}",
                body=message_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.CONTACT_RECEIVER_EMAIL],
            )
            email_msg.attach_alternative(html_content, "text/html")
            email_msg.send()
            
            logger.info(f"Email sent successfully from {email}")
            messages.success(request, "✅️ Email Sent !! Expect an email response from our support engineers within 24 hours.")

        except Exception as e:
            # Middleware extra data capture karel
            logger.error(f"Critical SMTP Error: {str(e)}", extra={
                'ip': ip, 'path': request.path, 'method': 'POST'
            })
            
            # Debugging check
            if settings.DEBUG:
                messages.error(request, f"🛠️ DEBUG: {str(e)}")
            else:
                messages.error(request, "⚠️ System busy. Please try sending the email again later.")

        return redirect('contact') 

    return render(request, "pages/contact.html", context)