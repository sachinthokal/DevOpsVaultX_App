import json
import razorpay
import logging
import os
import random
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse, FileResponse, HttpResponseNotFound
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F, Q
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from products.models import Product
from django.core.cache import cache
from .models import Payment

# Logger and Razorpay Client Setup
logger = logging.getLogger(__name__)
client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

# ======================
# 1. BUY PRODUCT (Fixed: Random ID & Credit Reset)
# ======================
def buy_product(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    
    if not request.session.session_key:
        request.session.create()
    session_id = request.session.session_key

    # १. नाव/ईमेल मिळवण्याचा प्रयत्न (POST > Session)
    customer_email = request.POST.get('email') or request.session.get('customer_email')
    customer_name = request.POST.get('customer_name') or request.session.get('customer_name')

    # २. जर अजूनही नाव मिळालं नसेल (Buy Again केस), तर DB मधून मागील रेकॉर्ड शोधा
    if not customer_name or not customer_email:
        last_payment = Payment.objects.filter(session_id=session_id).exclude(customer_name__isnull=True).exclude(customer_name="").order_by('-created_at').first()
        if last_payment:
            customer_name = customer_name or last_payment.customer_name
            customer_email = customer_email or last_payment.email

    # ३. भविष्यासाठी सेशन अपडेट करा
    request.session['customer_email'] = customer_email
    request.session['customer_name'] = customer_name

    # रिन्यूअल तपासणी: या ईमेलवर आधी यशस्वी पेमेंट झाले आहे का?
    is_renewal_payment = Payment.objects.filter(
        email=customer_email, 
        product=product, 
        status="SUCCESS"
    ).exists()

    # ४. FREE PRODUCT LOGIC
    if product.price == 0:
        # random.randint(1000, 9999) वापरलाय जेणेकरून ID unique राहील
        unique_order_id = f"FREE_{product.id}_{session_id[:5]}_{random.randint(1000,9999)}"
        
        Payment.objects.create(
            product=product, 
            session_id=session_id,
            email=customer_email,
            customer_name=customer_name,
            razorpay_order_id=unique_order_id,
            amount=0,
            is_renewal=is_renewal_payment, # इथे रिन्यूअल मार्क करा
            status="SUCCESS", 
            paid=True, 
            download_limit=5, 
            download_used=0, # नवीन खरेदीसाठी क्रेडिट्स रिसेट
            is_active=True    # नवीन खरेदी असल्यामुळे ऍक्टिव्ह असणे गरजेचे आहे
        )
        request.session[f"paid_{pk}"] = True
        # payment_result वर रिडायरेक्ट करा जेणेकरून UI आणि टोस्ट दिसेल
        return redirect(reverse("payments:payment_result", args=[pk]))

    # ५. PAID PRODUCT LOGIC
    amount = int(product.price * 100)
    # Razorpay order create
    razorpay_order = client.order.create({
        "amount": amount, 
        "currency": "INR", 
        "receipt": f"p_{product.id}_{random.randint(10,99)}", 
        "payment_capture": 1
    })

    # पेमेंट रेकॉर्ड तयार करा (Customer डेटासह)
    Payment.objects.create(
        product=product, 
        session_id=session_id, 
        email=customer_email, 
        customer_name=customer_name,
        razorpay_order_id=razorpay_order["id"], 
        amount=amount,
        is_renewal=is_renewal_payment, # इथे रिन्यूअल मार्क करा
        status="INIT", 
        download_limit=5, 
        download_used=0 # सुरुवातीला ० ठेवा
    )

    return render(request, "payments/payment.html", {
        "product": product, 
        "amount": amount, 
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": razorpay_order["id"], 
        "is_free": False,
        "customer_email": customer_email, 
        "customer_name": customer_name,
    })
# ======================
# 2. PAYMENT SUCCESS HANDLER
# ======================
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
        
    except razorpay.errors.SignatureVerificationError:
        payment.status = "FAILED"
        payment.save()
        return redirect(reverse("payments:payment_result", args=[pk]))

    if c_email:
        send_payment_success_email(c_email, product.title, c_name)

    request.session[f"paid_{pk}"] = True
    return redirect(reverse("payments:payment_result", args=[pk]))

# ======================
# 3. SECURE DOWNLOAD (Credit Logic)
# ======================
def download_file(request, pk):
    session_id = request.session.session_key
    session_email = request.session.get('customer_email')
    user_email = request.user.email if request.user.is_authenticated else None
    
    search_query = Q(session_id=session_id)
    if session_email: search_query |= Q(email=session_email)
    if user_email: search_query |= Q(email=user_email)

    is_forcing = request.GET.get('force_download') == '1'

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and not is_forcing:
        payment = Payment.objects.filter(search_query, product_id=pk, status="SUCCESS", is_active=True, download_used__lt=F('download_limit')).order_by('-created_at').first()
        if not payment:
            return JsonResponse({"status": "error", "message": "Limit Exceeded"}, status=400)

        payment.download_used += 1
        if payment.download_used >= payment.download_limit: payment.is_active = False
        payment.save()
        return JsonResponse({"status": "success", "download_url": f"/products/{pk}/download/?force_download=1"})

    if is_forcing:
        if not Payment.objects.filter(search_query, product_id=pk, status="SUCCESS").exists():
            return HttpResponseForbidden()
        product = get_object_or_404(Product, pk=pk)
        response = FileResponse(open(product.file.path, "rb"), as_attachment=True)
        response["Content-Disposition"] = f'attachment; filename="{os.path.basename(product.file.path)}"'
        return response
    return redirect('products:detail', pk=pk)

# ======================
# 4. RETRY & FAILURE
# ======================
@csrf_exempt
def payment_failed(request):
    order_id = request.POST.get("order_id")
    Payment.objects.filter(razorpay_order_id=order_id).update(status="FAILED")
    return JsonResponse({"retry": True}, status=402)

def retry_payment(request, order_id):
    old = get_object_or_404(Payment, razorpay_order_id=order_id, status="FAILED")
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
    except: return HttpResponse(status=400)

def payment_result(request, pk):
    product = get_object_or_404(Product, pk=pk)
    db_paid = Payment.objects.filter(product=product, session_id=request.session.session_key, status="SUCCESS").exists()
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
            send_mail(f"OTP: {otp}", f"Your OTP is {otp}", settings.EMAIL_HOST_USER, [email], html_message=render_to_string('emails/otp_email.html', {'otp': otp}))
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
            return JsonResponse({"status": "success"})
        return JsonResponse({"status": "error"}, status=400)
    return HttpResponseForbidden()

# ======================
# 7. EMAIL UTILITY
# ======================
def send_payment_success_email(u_email, p_title, c_name):
    try:
        html = render_to_string('emails/payment_success_email.html', {'product_title': p_title, 'customer_name': c_name or "Developer"})
        msg = EmailMultiAlternatives(f'Confirmed: {p_title}', strip_tags(html), settings.EMAIL_HOST_USER, [u_email])
        msg.attach_alternative(html, "text/html")
        msg.send()
    except Exception as e: logger.error(e)