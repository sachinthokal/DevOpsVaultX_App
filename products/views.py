from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, HttpResponseForbidden
from django.urls import reverse
from django.utils.http import http_date
from .models import Product
import os, time

# ======================
# Home Page
# ======================
def home(request):
    products = Product.objects.filter(is_active=True).order_by('-created_at')[:3]
    return render(request, 'home.html', {'products': products})


# ======================
# Products List Page
# ======================
def product_list(request):
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'products/product_list.html', {'products': products})


# ======================
# Product Detail Page
# ======================
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    return render(request, 'products/product_detail.html', {'product': product})


# ======================
# Buy Now (Redirects to Razorpay via payments app)
# ======================
def buy_now(request, pk):
    """
    This view can be OPTIONAL.
    Ideally Buy Now should redirect to payments app.
    """
    product = get_object_or_404(Product, pk=pk, is_active=True)
    return redirect('payments:buy_product', pk=product.id)


# ======================
# Payment Success Callback
# ======================
def confirm_payment(request, pk):
    """
    Called only after successful payment
    Marks session as paid
    """
    request.session[f'paid_{pk}'] = True
    return redirect('products:download_file', pk=pk)


# ======================
# Secure File Download
# ======================
def download_file(request, pk):

    session_key = f"paid_{pk}"

    if not request.session.get(session_key):
        return HttpResponseForbidden("Payment not completed")

    product = get_object_or_404(Product, pk=pk, is_active=True)

    if not product.file:
        return HttpResponseForbidden("File not available")

    file_path = product.file.path

    if not os.path.exists(file_path):
        return HttpResponseForbidden("File missing")

    response = FileResponse(
        open(file_path, "rb"),
        as_attachment=True,
        filename=os.path.basename(file_path)
    )

    # 🔐 prevent caching / re-download
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = http_date(time.time() - 3600)

    # 🔐 one-time download
    del request.session[session_key]

    return response


def payment_result(request, pk):
    session_key = f"paid_{pk}"
    product = get_object_or_404(Product, pk=pk, is_active=True)

    if request.session.get(session_key):
        # Payment successful
        status = "success"
        file_url = reverse("products:download_file", args=[pk])
    else:
        # Payment failed / session expired
        status = "failed"
        file_url = None

    return render(request, "products/payment_result.html", {
        "status": status,
        "file_url": file_url,
        "session_key": session_key
    })

