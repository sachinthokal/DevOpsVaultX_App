import json
import razorpay
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from products.models import Product
from .models import Payment

# Razorpay Client Initialization
client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

from django.db.models import F
from payments.models import Payment # बरोबर इम्पोर्ट असल्याची खात्री करा

# ======================
# BUY PRODUCT
# ======================
def buy_product(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    
    # Session ID मिळवा किंवा तयार करा
    if not request.session.session_key:
        request.session.create()
    session_id = request.session.session_key

    # STEP 2: POST मधून ईमेल आणि नाव मिळवा (जे आपण फॉर्ममध्ये अ‍ॅड करणार आहोत)
    customer_email = request.POST.get('email')
    customer_name = request.POST.get('customer_name')

    # 1. जर प्रॉडक्ट FREE असेल तर
    if product.price == 0:
        # Session ID नुसार आधीच एन्ट्री आहे का ते तपासा
        payment = Payment.objects.filter(
            product=product, 
            session_id=session_id
        ).first()

        if not payment:
            # नवीन युजर असेल तर एन्ट्री करा (ईमेल आणि नावासह)
            Payment.objects.create(
                product=product,
                session_id=session_id,
                email=customer_email,        # 🔥 ईमेल सेव्ह केला
                customer_name=customer_name, # 🔥 नाव सेव्ह केले
                razorpay_order_id=f"FREE_{product.id}",
                amount=0,
                status="SUCCESS",
                paid=True
            )
            # टीप: फ्री प्रॉडक्टसाठी ईमेल पाठवण्यासाठी इथे send_payment_success_email कॉल करू शकता
        else:
            # जुनाच युजर पुन्हा आला असेल तर फक्त क्लिक काउंट वाढवा आणि माहिती अपडेट करा
            payment.retry_count = F('retry_count') + 1
            if customer_email: payment.email = customer_email
            if customer_name: payment.customer_name = customer_name
            payment.save()

        return render(request, "payments/payment.html", {
        "product": product,
        "is_free": True,
        "razorpay_order_id": "FREE_ORDER", # Dummy ID dya jyamule error yenar nahi
    })

    # 2. जर प्रॉडक्ट PAID असेल तर
    amount = int(product.price * 100)
    razorpay_order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "receipt": f"product_{product.id}",
        "payment_capture": 1
    })

    # Paid पेमेंटसाठी सुद्धा session_id, ईमेल आणि नाव साठवून ठेवा
    Payment.objects.create(
        product=product,
        session_id=session_id,
        email=customer_email,        # 🔥 ईमेल सेव्ह केला
        customer_name=customer_name, # 🔥 नाव सेव्ह केले
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
        "customer_email": customer_email, # टेम्पलेटमध्ये वापरण्यासाठी
        "customer_name": customer_name,
    })

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponseForbidden
# ======================
# PAYMENT SUCCESS (Final Fixed Version)
# ======================
def payment_success(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()

    product = get_object_or_404(Product, pk=pk)
    session_id = request.session.session_key
    
    # ✅ फ्रंटएंड (Swal Popup) मधून आलेला डेटा मिळवा
    customer_name = request.POST.get('customer_name')
    customer_email = request.POST.get('email')

    # 1. जर प्रॉडक्ट FREE असेल तर
    if product.price == 0:
        payment = Payment.objects.filter(
            product=product, 
            session_id=session_id
        ).first()

        if payment:
            payment.status = "SUCCESS"
            payment.paid = True
            payment.retry_count = 0 
            
            # ✅ फ्री प्रॉडक्टसाठी पण ईमेल/नाव अपडेट करा
            if customer_name: payment.customer_name = customer_name
            if customer_email: payment.email = customer_email
            payment.save()

            # 🔥 ईमेल पाठवा (लॉगिन असेल तर युजरचा, नसेल तर फॉर्ममधला)
            recipient_email = customer_email or (request.user.email if request.user.is_authenticated else None)
            recipient_name = customer_name or (request.user.get_full_name() if request.user.is_authenticated else "Developer")

            if recipient_email:
                try:
                    send_payment_success_email(recipient_email, product.title, recipient_name)
                except:
                    pass

        request.session[f"paid_{pk}"] = True
        return redirect(reverse("payments:payment_result", args=[pk]))

    # 2. जर प्रॉडक्ट PAID असेल तर (Razorpay Flow)
    razorpay_order_id = request.POST.get("razorpay_order_id")
    
    payment = Payment.objects.filter(
        razorpay_order_id=razorpay_order_id,
        product_id=pk
    ).first()

    if not payment:
        return HttpResponseForbidden("Payment record not found.")

    try:
        # Verify Razorpay Signature
        client.utility.verify_payment_signature({
            "razorpay_payment_id": request.POST.get("razorpay_payment_id"),
            "razorpay_order_id": razorpay_order_id,
            "razorpay_signature": request.POST.get("razorpay_signature"),
        })

        payment.razorpay_payment_id = request.POST.get("razorpay_payment_id")
        payment.razorpay_signature = request.POST.get("razorpay_signature")
        payment.status = "SUCCESS"
        payment.paid = True
        payment.retry_count = 0 
        
        # ✅ पेड सक्सेस झाल्यावर ईमेल आणि नाव डेटाबेसमध्ये साठवा
        if customer_name: payment.customer_name = customer_name
        if customer_email: payment.email = customer_email
        payment.save()

        # 🔥 SEND PREMIUM EMAIL
        recipient_email = customer_email or (request.user.email if request.user.is_authenticated else None)
        recipient_name = customer_name or (request.user.get_full_name() if request.user.is_authenticated else "Developer")

        if recipient_email:
            try:
                send_payment_success_email(recipient_email, product.title, recipient_name)
            except:
                pass

        request.session[f"paid_{pk}"] = True
        return redirect(reverse("payments:payment_result", args=[pk]))

    except razorpay.errors.SignatureVerificationError:
        payment.status = "FAILED"
        payment.save()
        return redirect(reverse("payments:payment_result", args=[pk]))

# ======================
# PAYMENT FAILED
# ======================
@csrf_exempt
def payment_failed(request):
    order_id = request.POST.get("order_id")
    error_msg = request.POST.get("error_msg", "Payment Failed") 

    Payment.objects.filter(razorpay_order_id=order_id).update(status="FAILED")

    response = JsonResponse({"retry": True}, status=402)
    response.reason_phrase = error_msg 
    return response

# ======================
# RETRY PAYMENT
# ======================
def retry_payment(request, order_id):
    old = get_object_or_404(Payment, razorpay_order_id=order_id, status="FAILED")
    session_id = request.session.session_key

    new_order = client.order.create({
        "amount": old.amount,
        "currency": "INR",
        "receipt": f"retry_{old.product.id}",
        "payment_capture": 1
    })

    Payment.objects.create(
        product=old.product,
        session_id=session_id,
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
# 🔐 RAZORPAY WEBHOOK
# ======================
@csrf_exempt
def razorpay_webhook(request):
    payload = request.body
    signature = request.headers.get("X-Razorpay-Signature")

    try:
        client.utility.verify_webhook_signature(
            payload,
            signature,
            settings.RAZORPAY_WEBHOOK_SECRET
        )
    except razorpay.errors.SignatureVerificationError:
        return HttpResponse("Invalid Signature", status=400)

    data = json.loads(payload)
    if data.get("event") == "payment.captured":
        entity = data["payload"]["payment"]["entity"]
        order_id = entity["order_id"]
        
        Payment.objects.filter(razorpay_order_id=order_id).update(
            razorpay_payment_id=entity["id"],
            status="SUCCESS",
            paid=True
        )

    return HttpResponse(status=200)

# ======================
# 🔐 SEND_PAYMENT_SUCCESS_EMAIL
# ======================
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

# Logger सेट करा जेणेकरून आपण त्रुटी पाहू शकू
logger = logging.getLogger(__name__)

def send_payment_success_email(user_email, product_title, customer_name):
    print(f"DEBUG: Attempting to send email to {user_email} for {product_title}...") # टर्मिनलमध्ये दिसेल
    
    subject = f'Order Confirmed: {product_title} - DevOpsVaultX'
    from_email = settings.EMAIL_HOST_USER
    to = [user_email]

    try:
        # १. HTML कंटेंट तयार करा
        html_content = render_to_string('emails/payment_success_email.html', {
            'product_title': product_title,
            'customer_name': customer_name or "Developer",
        })
        
        text_content = strip_tags(html_content) 

        # २. ई-मेल ऑब्जेक्ट तयार करा
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")

        # ३. ई-मेल पाठवा
        msg.send(fail_silently=False) # fail_silently=False केल्याने एरर टर्मिनलमध्ये दिसेल
        
        print(f"SUCCESS: Email sent successfully to {user_email}")
        return True

    except Exception as e:
        # ४. जर काही एरर आला तर तो प्रिंट करा
        print(f"ERROR: Failed to send email! Details: {e}")
        logger.error(f"Email sending failed: {e}")
        return False
    

# ======================
# Payment Result Page
# ======================
def payment_result(request, pk):
    session_key = f"paid_{pk}"
    product = get_object_or_404(Product, pk=pk, is_active=True)

    # 1. Check kara product Free aahe ka
    is_free = product.price == 0

    # 2. Database check (Paid products sathi)
    db_paid = Payment.objects.filter(product=product, status="SUCCESS", paid=True).exists()

    # 3. Success condition: Jar Free asel OR Session madhe entry asel OR DB madhe entry asel
    if is_free or request.session.get(session_key) or db_paid:
        status = "success"
        file_url = reverse("products:download_file", args=[pk])
        # Download access sathi session set kara
        request.session[session_key] = True 
    else:
        status = "failed"
        file_url = None
    
    return render(request, "payments/payment_result.html", {
        "status": status,
        "product": product,
        "file_url": file_url,
        "is_free": product.price == 0, # <--- He add kara
    })