import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Product
from payments.models import Payment

# ======================
# Home Page
# ======================
def home(request):
    # Top 3 active products
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
# Buy Now
# ======================
def buy_now(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    return redirect('payments:buy_product', pk=product.id)

# ======================
# Payment Success Callback (Session Based)
# ======================
def confirm_payment(request, pk):
    request.session[f'paid_{pk}'] = True
    return redirect('products:download_file', pk=pk)

# ======================
# Secure File Download
# ======================
@login_required
def download_file(request, pk):
    session_key = f"paid_{pk}"
    
    # Security check: Session OR Database
    db_paid = Payment.objects.filter(product_id=pk, status="SUCCESS", paid=True).exists()

    if not request.session.get(session_key) and not db_paid:
        return HttpResponseForbidden("Payment not completed")

    product = get_object_or_404(Product, pk=pk, is_active=True)
    
    if not product.file or not os.path.exists(product.file.path):
        return HttpResponseForbidden("File not available or missing")

    response = FileResponse(open(product.file.path, "rb"), as_attachment=True)
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.reason_phrase = f"File Download Started: {product.title}"
    # Cleanup session after download start
    if session_key in request.session:
        del request.session[session_key]
        
    return response

# ======================
# Payment Result Page
# ======================
def payment_result(request, pk):
    session_key = f"paid_{pk}"
    product = get_object_or_404(Product, pk=pk, is_active=True)

    # Database check
    db_paid = Payment.objects.filter(product=product, status="SUCCESS", paid=True).exists()

    if request.session.get(session_key) or db_paid:
        status = "success"
        file_url = reverse("products:download_file", args=[pk])
        # Ensure session is persistent for download access
        request.session[session_key] = True 
    else:
        status = "failed"
        file_url = None

    return render(request, "products/payment_result.html", {
        "status": status,
        "product": product,
        "file_url": file_url,
    })