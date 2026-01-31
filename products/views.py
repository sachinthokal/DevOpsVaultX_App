from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.http import http_date
from .models import Product
from payments.models import Payment # ✅ Added Import
import os, time
import logging

logger = logging.getLogger(__name__)

# ======================
# Home Page
# ======================
def home(request):
    try:
        logger.info("Home page requested")
        products = Product.objects.filter(is_active=True).order_by('-created_at')[:3]
        return render(request, 'home.html', {'products': products})
    except Exception as e:
        logger.error("Error loading home page", exc_info=True)
        return render(request, 'home.html', {'products': []})

# ======================
# Products List Page
# ======================
def product_list(request):
    try:
        logger.info("Product list page requested")
        products = Product.objects.filter(is_active=True).order_by('-created_at')
        return render(request, 'products/product_list.html', {'products': products})
    except Exception as e:
        logger.error("Error fetching product list", exc_info=True)
        return render(request, 'products/product_list.html', {'products': []})

# ======================
# Product Detail Page
# ======================
def product_detail(request, pk):
    try:
        product = get_object_or_404(Product, pk=pk, is_active=True)
        return render(request, 'products/product_detail.html', {'product': product})
    except Exception as e:
        logger.error(f"Error viewing product {pk}", exc_info=True)
        return redirect('products:product_list')

# ======================
# Buy Now
# ======================
def buy_now(request, pk):
    try:
        product = get_object_or_404(Product, pk=pk, is_active=True)
        return redirect('payments:buy_product', pk=product.id)
    except Exception as e:
        logger.error(f"Error redirecting to payment for product {pk}", exc_info=True)
        return redirect('products:product_list')

# ======================
# Payment Success Callback (Session Based)
# ======================
def confirm_payment(request, pk):
    try:
        request.session[f'paid_{pk}'] = True
        return redirect('products:download_file', pk=pk)
    except Exception as e:
        logger.error(f"Error confirming payment for product {pk}", exc_info=True)
        return redirect('products:product_list')

# ======================
# Secure File Download
# ======================
@login_required
def download_file(request, pk):
    session_key = f"paid_{pk}"
    
    # ✅ Check DB as fallback for security
    db_paid = Payment.objects.filter(product_id=pk, status="SUCCESS", paid=True).exists()

    if not request.session.get(session_key) and not db_paid:
        return HttpResponseForbidden("Payment not completed")

    product = get_object_or_404(Product, pk=pk, is_active=True)
    if not product.file:
        return HttpResponseForbidden("File not available")

    file_path = os.path.abspath(product.file.path)
    if not os.path.exists(file_path):
        return HttpResponseForbidden("File missing")

    response = FileResponse(open(file_path, "rb"), as_attachment=True)
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    
    # Only delete session if it exists
    if session_key in request.session:
        del request.session[session_key]
        
    return response

# ======================
# Payment Result Page - FIXED
# ======================
def payment_result(request, pk):
    session_key = f"paid_{pk}"
    product = get_object_or_404(Product, pk=pk, is_active=True)

    # ✅ FIXED: Check both Session and Database
    db_paid = Payment.objects.filter(product=product, status="SUCCESS", paid=True).exists()

    if request.session.get(session_key) or db_paid:
        status = "success"
        file_url = reverse("products:download_file", args=[pk])
        # Ensure session is set if DB check passed
        request.session[session_key] = True 
    else:
        status = "failed"
        file_url = None

    return render(request, "products/payment_result.html", {
        "status": status,
        "product": product,
        "file_url": file_url,
    })