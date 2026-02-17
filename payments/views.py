import json
import razorpay
import logging
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from django.core.mail import EmailMultiAlternatives
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
# 1. BUY PRODUCT (Initial Entry)
# ======================
def buy_product(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    
    if not request.session.session_key:
        request.session.create()
    session_id = request.session.session_key

    # GET request वर फक्त पेमेंट पेज दाखवा, POST वर डेटा प्रोसेस करा (जर फॉर्म वापरत असाल तर)
    customer_email = request.POST.get('email')
    customer_name = request.POST.get('customer_name')

    # जर प्रॉडक्ट FREE असेल तर
    if product.price == 0:
        payment, created = Payment.objects.get_or_create(
            product=product, 
            session_id=session_id,
            defaults={
                'email': customer_email,
                'customer_name': customer_name,
                'razorpay_order_id': f"FREE_{product.id}_{session_id[:5]}",
                'amount': 0,
                'status': "SUCCESS",
                'paid': True
            }
        )
        if not created:
            payment.retry_count = F('retry_count') + 1
            payment.save()

        return render(request, "payments/payment.html", {
            "product": product,
            "is_free": True,
            "razorpay_order_id": "FREE_ORDER",
        })

    # जर प्रॉडक्ट PAID असेल तर Razorpay Order तयार करा
    amount = int(product.price * 100)
    razorpay_order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "receipt": f"product_{product.id}",
        "payment_capture": 1
    })

    # पेमेंट रेकॉर्ड तयार करा
    Payment.objects.create(
        product=product,
        session_id=session_id,
        email=customer_email,
        customer_name=customer_name,
        razorpay_order_id=razorpay_order["id"],
        amount=amount,
        status="INIT"
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
    session_id = request.session.session_key
    
    customer_name = request.POST.get('customer_name')
    customer_email = request.POST.get('email')

    # FREE Product Success Logic
    if product.price == 0:
        Payment.objects.filter(product=product, session_id=session_id).update(
            status="SUCCESS", 
            paid=True,
            customer_name=customer_name,
            email=customer_email
        )
    
    # PAID Product Razorpay Verification
    else:
        razorpay_order_id = request.POST.get("razorpay_order_id")
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
            payment.status = "SUCCESS"
            payment.paid = True
            payment.customer_name = customer_name
            payment.email = customer_email
            payment.save()
        except razorpay.errors.SignatureVerificationError:
            payment.status = "FAILED"
            payment.save()
            return redirect(reverse("payments:payment_result", args=[pk]))

    # Success Email पाठवा
    recipient_email = customer_email or (request.user.email if request.user.is_authenticated else None)
    recipient_name = customer_name or (request.user.get_full_name() if request.user.is_authenticated else "Developer")
    
    if recipient_email:
        send_payment_success_email(recipient_email, product.title, recipient_name)

    request.session[f"paid_{pk}"] = True
    return redirect(reverse("payments:payment_result", args=[pk]))

# ======================
# 3. RETRY & FAILURE HANDLERS
# ======================
@csrf_exempt
def payment_failed(request):
    order_id = request.POST.get("order_id")
    Payment.objects.filter(razorpay_order_id=order_id).update(status="FAILED")
    return JsonResponse({"retry": True}, status=402)

def retry_payment(request, order_id):
    old = get_object_or_404(Payment, razorpay_order_id=order_id, status="FAILED")
    
    new_order = client.order.create({
        "amount": old.amount,
        "currency": "INR",
        "receipt": f"retry_{old.product.id}",
        "payment_capture": 1
    })

    Payment.objects.create(
        product=old.product,
        session_id=request.session.session_key,
        razorpay_order_id=new_order["id"],
        amount=old.amount,
        retry_count=old.retry_count + 1,
        status="INIT"
    )
    return render(request, "payments/payment.html", {
        "product": old.product,
        "amount": old.amount,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": new_order["id"],
    })

# ======================
# 4. WEBHOOK & RESULTS
# ======================
@csrf_exempt
def razorpay_webhook(request):
    payload = request.body
    signature = request.headers.get("X-Razorpay-Signature")

    try:
        client.utility.verify_webhook_signature(payload, signature, settings.RAZORPAY_WEBHOOK_SECRET)
        data = json.loads(payload)
        if data.get("event") == "payment.captured":
            entity = data["payload"]["payment"]["entity"]
            Payment.objects.filter(razorpay_order_id=entity["order_id"]).update(
                razorpay_payment_id=entity["id"], status="SUCCESS", paid=True
            )
        return HttpResponse(status=200)
    except:
        return HttpResponse("Invalid Signature", status=400)

def payment_result(request, pk):
    product = get_object_or_404(Product, pk=pk)
    session_key = f"paid_{pk}"
    
    # Success Condition
    db_paid = Payment.objects.filter(product=product, session_id=request.session.session_key, status="SUCCESS").exists()
    
    if product.price == 0 or request.session.get(session_key) or db_paid:
        status, file_url = "success", reverse("products:download_file", args=[pk])
        request.session[session_key] = True 
    else:
        status, file_url = "failed", None
    
    return render(request, "payments/payment_result.html", {
        "status": status, "product": product, "file_url": file_url, "is_free": product.price == 0,
    })

# ======================
# 5. EMAIL UTILITY
# ======================
def send_payment_success_email(user_email, product_title, customer_name):
    subject = f'Order Confirmed: {product_title} - DevOpsVaultX'
    from_email = settings.EMAIL_HOST_USER
    
    try:
        html_content = render_to_string('emails/payment_success_email.html', {
            'product_title': product_title,
            'customer_name': customer_name or "Developer",
        })
        text_content = strip_tags(html_content) 
        msg = EmailMultiAlternatives(subject, text_content, from_email, [user_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"Email failure: {e}")
        return False
    
import random
from django.core.cache import cache
from django.core.mail import send_mail

# ... (तुमचे इतर इम्पोर्ट्स जसे आहेत तसेच राहतील)

# ======================
# 🔐 OTP SYSTEM (SEND & VERIFY) - हे अ‍ॅड करा
# ======================
@csrf_exempt
def send_otp(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get('email')
            otp = str(random.randint(100000, 999999))
            cache.set(f"otp_{email}", otp, timeout=300)

            # HTML Template Render करा
            context = {'otp': otp}
            html_message = render_to_string('emails/otp_email.html', context)
            plain_message = f"Your verification code is: {otp}. It is valid for 5 minutes."

            send_mail(
                subject="Verification Code: " + otp + " - DevOpsVaultX", # English Subject
                message=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                html_message=html_message, # हा HTML UI पाठवेल
                fail_silently=False,
            )
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return HttpResponseForbidden()



# ======================
# Verify OTP (Fixed with email_otp_verified)
# ======================
@csrf_exempt
def verify_otp(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get('email')  # हा नवीन ईमेल आहे
            user_otp = data.get('otp')
            is_update_request = data.get('is_update', False) 
            
            saved_otp = cache.get(f"otp_{email}")
            
            if saved_otp and str(saved_otp) == str(user_otp):
                if is_update_request:
                    session_id = request.session.session_key
                    if session_id:
                        # १. सध्याचा ईमेल (जो आता 'Old' होणार आहे) मिळवा
                        old_payment = Payment.objects.filter(
                            session_id=session_id, 
                            status="SUCCESS"
                        ).first()
                        
                        current_old_email = old_payment.email if old_payment else "Unknown"

                        # २. डेटाबेसमध्ये सर्व पेमेंट्स अपडेट करा (email_otp_verified सह)
                        Payment.objects.filter(
                            session_id=session_id, 
                            status="SUCCESS"
                        ).update(
                            old_email=current_old_email,     # जुना ईमेल सेव्ह होतोय
                            email=email,                    # नवीन ईमेल अपडेट होतोय
                            email_updated=True,             # ईमेल बदलल्याचा मार्क
                            email_otp_verified=True         # 🔥 आता हा ईमेल व्हेरिफाईड आहे!
                        )
                        
                        # ३. सर्वात महत्त्वाचे: Django Session अपडेट करा
                        request.session['customer_email'] = email
                        request.session.modified = True 
                        
                        return JsonResponse({"status": "success", "message": "Email Updated successfully!"})
                    else:
                        return JsonResponse({"status": "error", "message": "Session Expired"}, status=400)

                # नॉर्मल पेमेंट व्हेरिफिकेशनसाठी (जेव्हा युजर पहिल्यांदा येतो)
                cache.set(f"verified_{email}", True, timeout=600)
                return JsonResponse({"status": "success", "message": "Verified"})
            
            else:
                return JsonResponse({"status": "error", "message": "चुकीचा OTP!"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
            
    return HttpResponseForbidden()