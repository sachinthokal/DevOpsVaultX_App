import json
import razorpay
import logging
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from products.models import Product
from .models import Payment

logger = logging.getLogger(__name__)

client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

def get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0] if xff else request.META.get("REMOTE_ADDR")

# ======================
# BUY PRODUCT
# ======================
def buy_product(request, pk):
    logger.info(f"Starting buying product: {pk}")
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
# PAYMENT SUCCESS (Frontend) - FIXED
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

        # ✅ FIXED: Set session so payment_result can see it
        request.session[f"paid_{pk}"] = True

        logger.info(f"PAYMENT_SUCCESS {payment.razorpay_order_id}")
        return redirect(reverse("products:payment_result", args=[pk]))

    except razorpay.errors.SignatureVerificationError:
        payment.status = "FAILED"
        payment.save()
        logger.error(f"SIGNATURE_FAIL {payment.razorpay_order_id}")
        return redirect(reverse("products:payment_result", args=[pk]))

# ======================
# PAYMENT FAILED (AJAX)
# ======================
@csrf_exempt
def payment_failed(request):
    order_id = request.POST.get("order_id")

    Payment.objects.filter(
        razorpay_order_id=order_id
    ).update(status="FAILED")

    logger.error(f"PAYMENT_FAILED Order={order_id}")
    return JsonResponse({"retry": True}, status=402)

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

    return render(request, "payments/payment.html", {
        "product": old.product,
        "amount": old.amount,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": new_order["id"],
    })

# ======================
# 🔐 RAZORPAY WEBHOOK (FINAL)
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
        logger.error("INVALID WEBHOOK SIGNATURE")
        return HttpResponse(status=400)

    data = json.loads(payload)
    event = data.get("event")

    if event == "payment.captured":
        entity = data["payload"]["payment"]["entity"]
        order_id = entity["order_id"]
        payment_id = entity["id"]

        Payment.objects.filter(
            razorpay_order_id=order_id
        ).update(
            razorpay_payment_id=payment_id,
            status="SUCCESS",
            paid=True
        )

        logger.info(f"WEBHOOK_SUCCESS Order={order_id}")

    return HttpResponse(status=200)