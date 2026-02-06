import json
import razorpay
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from products.models import Product
from .models import Payment

# Razorpay Client Initialization
client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

# ======================
# BUY PRODUCT
# ======================
def buy_product(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    amount = int(product.price * 100)

    razorpay_order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "receipt": f"product_{product.id}",
        "payment_capture": 1
    })

    Payment.objects.create(
        product=product,
        razorpay_order_id=razorpay_order["id"],
        amount=amount,
        status="INIT"
    )

    return render(request, "payments/payment.html", {
        "product": product,
        "amount": amount,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": razorpay_order["id"],
    })

# ======================
# PAYMENT SUCCESS (Frontend)
# ======================
def payment_success(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()

    payment = get_object_or_404(
        Payment,
        razorpay_order_id=request.POST.get("razorpay_order_id"),
        product_id=pk
    )

    try:
        # Verify Razorpay Signature
        client.utility.verify_payment_signature({
            "razorpay_payment_id": request.POST.get("razorpay_payment_id"),
            "razorpay_order_id": request.POST.get("razorpay_order_id"),
            "razorpay_signature": request.POST.get("razorpay_signature"),
        })

        payment.razorpay_payment_id = request.POST.get("razorpay_payment_id")
        payment.razorpay_signature = request.POST.get("razorpay_signature")
        payment.status = "SUCCESS"
        payment.paid = True
        payment.save()

        # Set session for download access
        request.session[f"paid_{pk}"] = True
        response = redirect(reverse("products:payment_result", args=[pk]))
        # 👇 He add kara, jemule log madhe "Found" chya jagi he disel
        response.reason_phrase = f"Payment Successful for Product {pk}"
        return response

    except razorpay.errors.SignatureVerificationError:
        payment.status = "FAILED"
        payment.save()
        # Middleware will automatically log the 302 redirect. 
        # If you want to show 'Signature Fail' in logs, set reason_phrase before redirect:
        response = redirect(reverse("products:payment_result", args=[pk]))
        response.reason_phrase = f"Payment FAILED for Product {pk}"
        return response

# ======================
# PAYMENT FAILED (AJAX Call from Frontend)
# ======================
@csrf_exempt
def payment_failed(request):
    order_id = request.POST.get("order_id")
    error_msg = request.POST.get("error_msg", "Payment Failed") 

    Payment.objects.filter(razorpay_order_id=order_id).update(status="FAILED")

    response = JsonResponse({"retry": True}, status=402)
    response.reason_phrase = error_msg  # Captured by Middleware Audit Log
    return response

# ======================
# RETRY PAYMENT
# ======================
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
        razorpay_order_id=new_order["id"],
        amount=old.amount,
        retry_count=old.retry_count + 1,
        status="INIT"
    )
    response = render(request, "payments/payment.html", {
        "product": old.product,
        "amount": old.amount,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": new_order["id"],
    })
    response.reason_phrase = f"Retry Payment for Product {order_id}"
    return response

# ======================
# 🔐 RAZORPAY WEBHOOK (Server-to-Server)
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
        # Webhook logs are better handled manually since they don't have a standard user request flow
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