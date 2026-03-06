import json
import razorpay
import logging
import os
import random
import datetime
import threading
import uuid
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse, FileResponse, HttpResponseNotFound
from django.views.decorators.cache import never_cache
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F, Q
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from products.models import Product
from django.core.cache import cache
from .models import Payment
from dashboard.models import SystemLog

# Logger and Razorpay Client Setup
logger = logging.getLogger(__name__)
client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

# ======================
# 0. PAYMENT PRODUCT INIT PAGE
# ======================
def some_index_view(request):
    return redirect('/')

# ======================
# 1. BUY PRODUCT (Fixed: Random ID & Credit Reset)
# ======================
def buy_product(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    
    if not request.session.session_key:
        request.session.create()
    session_id = request.session.session_key

    # 1. User details fix kara
    customer_email = None
    customer_name = None
    current_user = None

    if request.user.is_authenticated:
        current_user = request.user  # Ha 'user' field madhe save karaycha aahe
        customer_email = request.user.email
        customer_name = request.user.first_name + " " + request.user.last_name if request.user.first_name and request.user.last_name else request.user.username
    else:
        customer_email = request.POST.get('email') or request.session.get('customer_email')
        customer_name = request.POST.get('customer_name') or request.session.get('customer_name')

    # Session data update kara
    request.session['customer_email'] = customer_email
    request.session['customer_name'] = customer_name

    # Renewal check
    is_renewal_payment = Payment.objects.filter(
        email=customer_email, 
        product=product, 
        status="SUCCESS"
    ).exists()

    # 2. FREE PRODUCT LOGIC (With User Link)
    if product.price == 0:
        
        # Current Date dynamic ghenyasathi (Format: DDMMYYYY)
        # Example: 28022026
        date_str = datetime.datetime.now().strftime("%d%m%Y") 
        
        # 1. Unique Order ID Format: ORD-FREE-28022026-XXXX
        unique_order_id = f"ORD-FREE-{date_str}-{uuid.uuid4().hex[:8].upper()}"
        
        # 2. Dummy Payment ID Format: PAY-FREE-28022026-XXXXXXXXXX
        dummy_payment_id = f"PAY-FREE-{date_str}-{uuid.uuid4().hex[:8].upper()}"
        
        Payment.objects.create(
            user=current_user,  # ITHE USER LINK KELA AAHE
            product=product, 
            session_id=session_id,
            email=customer_email,
            customer_name=customer_name,
            razorpay_order_id=unique_order_id,
            razorpay_payment_id=dummy_payment_id,  # Free Dummy ID
            amount=0,
            is_renewal=is_renewal_payment,
            status="SUCCESS", 
            paid=True, 
            download_limit=5, 
            download_used=0,
            is_active=True
        )
        request.session[f"paid_{pk}"] = True
        return redirect(reverse("payments:payment_result", args=[pk]))

    # 3. PAID PRODUCT LOGIC (With User Link)
    amount = int(product.price * 100)
    razorpay_order = client.order.create({
        "amount": amount, 
        "currency": "INR", 
        "receipt": f"p_{product.id}_{random.randint(10,99)}", 
        "payment_capture": 1
    })

    Payment.objects.create(
        user=current_user,  # ITHE USER LINK KELA AAHE
        product=product, 
        session_id=session_id, 
        email=customer_email, 
        customer_name=customer_name,
        razorpay_order_id=razorpay_order["id"], 
        amount=amount,
        is_renewal=is_renewal_payment,
        status="INIT", 
        download_limit=5, 
        download_used=0
    )

    return render(request, "payments/payment.html", {
        "product": product, 
        "amount": amount, 
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": razorpay_order["id"], 
        "customer_email": customer_email, 
        "customer_name": customer_name,
    })

# ======================
# 2. PAYMENT SUCCESS HANDLER
# ======================
@never_cache
def payment_success(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()

    product = get_object_or_404(Product, pk=pk)
    razorpay_order_id = request.POST.get("razorpay_order_id")
    
    # नाव आणि ईमेल पुन्हा एकदा खात्री करून घ्या
    c_name = request.POST.get('customer_name') or request.session.get('customer_name')
    c_email = request.POST.get('email') or request.session.get('customer_email')

    payment = Payment.objects.filter(razorpay_order_id=razorpay_order_id).first()
    if not payment:
        return HttpResponseForbidden("Payment record not found.")

    try:
        client.utility.verify_payment_signature({
            "razorpay_payment_id": request.POST.get("razorpay_payment_id"),
            "razorpay_order_id": razorpay_order_id,
            "razorpay_signature": request.POST.get("razorpay_signature"),
        })
        payment.razorpay_payment_id = request.POST.get("razorpay_payment_id")
        payment.razorpay_signature = request.POST.get("razorpay_signature")
        payment.status, payment.paid, payment.is_active = "SUCCESS", True, True
        
        # जर पेमेंट एन्ट्री वेळी नाव नसेल तर इथे अपडेट करा
        if not payment.customer_name: payment.customer_name = c_name
        if not payment.email: payment.email = c_email
        payment.save()

        # ==========================================
        # DYNAMIC LOG START: PAYMENT SUCCESS
        # ==========================================
        amt_rupees = payment.amount / 100
        SystemLog.objects.create(
            message=f"Payment SUCCESS: ₹{amt_rupees} received from {c_name} for {product.title}",
            log_type="Payment"
        )
        # ==========================================
        
    except razorpay.errors.SignatureVerificationError:
        payment.status = "FAILED"
        payment.save()

        # ==========================================
        # DYNAMIC LOG: SIGNATURE FAILED
        # ==========================================
        SystemLog.objects.create(
            message=f"Critical: Signature mismatch for Order #{razorpay_order_id}",
            log_type="Error"
        )
        # ==========================================

        return redirect(reverse("payments:payment_result", args=[pk]))

    # EMAIL CALL FIX
    if c_email:
        # Threading vapra jevane page fast reload hoil
        threading.Thread(
            target=send_payment_success_email, 
            args=(c_email, product.title, c_name)
        ).start()

    request.session[f"paid_{pk}"] = True
    return redirect(reverse("payments:payment_result", args=[pk]))


# ======================
# 4. RETRY & FAILURE
# ======================
@csrf_exempt
def payment_failed(request):
    order_id = request.POST.get("order_id")
    Payment.objects.filter(razorpay_order_id=order_id).update(status="FAILED")
    # DYNAMIC LOG: PAYMENT FAILED
    SystemLog.objects.create(
        message=f"Transaction Failed: Order ID #{order_id} was unsuccessful",
        log_type="Error"
    )
    return JsonResponse({"retry": True}, status=402)

def retry_payment(request, order_id):
    old = get_object_or_404(Payment, razorpay_order_id=order_id, status="FAILED")
    # DYNAMIC LOG: RETRY ATTEMPT
    SystemLog.objects.create(
        message=f"Retry Initiated: User attempting payment again for {old.product.title}",
        log_type="System"
    )
    new_order = client.order.create({"amount": old.amount, "currency": "INR", "receipt": f"retry_{old.product.id}", "payment_capture": 1})
    Payment.objects.create(product=old.product, session_id=request.session.session_key, razorpay_order_id=new_order["id"], amount=old.amount, status="INIT", email=old.email, customer_name=old.customer_name)
    return render(request, "payments/payment.html", {"product": old.product, "amount": old.amount, "razorpay_key_id": settings.RAZORPAY_KEY_ID, "razorpay_order_id": new_order["id"]})

# ======================
# 5. WEBHOOK & RESULTS
# ======================
@csrf_exempt
def razorpay_webhook(request):
    payload, sig = request.body, request.headers.get("X-Razorpay-Signature")
    try:
        client.utility.verify_webhook_signature(payload, sig, settings.RAZORPAY_WEBHOOK_SECRET)
        data = json.loads(payload)
        if data.get("event") == "payment.captured":
            Payment.objects.filter(razorpay_order_id=data["payload"]["payment"]["entity"]["order_id"]).update(status="SUCCESS", paid=True, is_active=True)
        return HttpResponse(status=200)
    except Exception as e:
        logger.error(f"Webhook Error: {str(e)}")
        return HttpResponse(status=400)

# ======================
# 5. PAYMENT RESULT
# ======================
def payment_result(request, pk):
    product = get_object_or_404(Product, pk=pk)
    db_paid = Payment.objects.filter(product=product, session_id=request.session.session_key, status="SUCCESS").exists()
    logger.info("Payment Result: " + ("success" if db_paid else "failed"))
    return render(request, "payments/payment_result.html", {"status": "success" if db_paid else "failed", "product": product, "is_free": product.price == 0})

# ======================
# 6. OTP SYSTEM
# ======================
@csrf_exempt
def send_otp(request):
    if request.method == "POST":
        try:
            email = json.loads(request.body).get('email')
            otp = str(random.randint(100000, 999999))
            cache.set(f"otp_{email}", otp, timeout=300)
            send_mail(f"DEVOPSVAULTX - VERIFICATION CODE : {otp}", f"Your OTP is {otp}", settings.EMAIL_HOST_USER, [email], html_message=render_to_string('emails/otp_email.html', {'otp': otp}))
            logger.info(f"OTP SENT TO: {email}")
            return JsonResponse({"status": "success"})
        except Exception as e: return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return HttpResponseForbidden()

@csrf_exempt
def verify_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email, user_otp, is_upd = data.get('email'), data.get('otp'), data.get('is_update', False)
        if str(cache.get(f"otp_{email}")) == str(user_otp):
            if is_upd and request.session.session_key:
                old_p = Payment.objects.filter(session_id=request.session.session_key, status="SUCCESS").first()
                Payment.objects.filter(session_id=request.session.session_key, status="SUCCESS").update(old_email=old_p.email if old_p else "", email=email, email_updated=True, email_otp_verified=True)
                request.session['customer_email'] = email
            logger.info(f"OTP VERIFIED: {email}")
            return JsonResponse({"status": "success"})
        return JsonResponse({"status": "error"}, status=400)
    return HttpResponseForbidden()

# ======================
# 7. EMAIL UTILITY
# ======================
def send_payment_success_email(u_email, p_title, c_name):
    try:
        # 1. Context data prepare kara
        context = {
            'product_title': p_title, 
            'customer_name': c_name or "Developer"
        }
        
        # 2. HTML render kara
        html_content = render_to_string('emails/payment_success_email.html', context)
        text_content = strip_tags(html_content) # Plain text fallback sathi
        
        # 3. Email Object banva
        subject = f"Order Confirmed! {p_title} has been added to your vault 🔐"
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[u_email]
        )
        
        # 4. HTML version attach kara
        msg.attach_alternative(html_content, "text/html")
        
        # 5. Send (fail_silently=False mule error samajto)
        msg.send(fail_silently=False)
        logger.info(f"SUCCESS: Email sent to {u_email} for {p_title}")
    except Exception as e:
        logger.error(f"Email Error for {u_email}: {str(e)}")