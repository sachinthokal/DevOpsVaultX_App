from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from products.models import Product
from .models import Payment
import razorpay

# Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# ======================
# Buy Product (Create Razorpay Order)
# ======================
def buy_product(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)

    amount = product.price * 100  # INR → paise

    razorpay_order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "receipt": f"order_{product.id}",
        "payment_capture": 1
    })

    Payment.objects.create(
        product=product,
        razorpay_order_id=razorpay_order["id"]
    )

    context = {
        "product": product,
        "amount": amount,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": razorpay_order["id"],
    }

    return render(request, "payments/payment.html", context)


@csrf_exempt
def payment_success(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden("Invalid request method")

    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_signature = request.POST.get("razorpay_signature")

    if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
        return HttpResponse("Invalid payment response", status=400)

    payment = get_object_or_404(Payment, razorpay_order_id=razorpay_order_id, product_id=pk)

    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        })
    except razorpay.errors.SignatureVerificationError:
        return redirect(reverse("products:payment_result", args=[pk]))  # failure

    payment.razorpay_payment_id = razorpay_payment_id
    payment.paid = True
    payment.save()

    # Set session key
    request.session[f"paid_{pk}"] = True

    # Redirect to payment_result page
    return redirect(reverse("products:payment_result", args=[pk]))

