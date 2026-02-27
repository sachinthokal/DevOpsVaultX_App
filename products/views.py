import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, JsonResponse
from django.db.models import Q, F
from payments.models import Payment
from django.contrib import messages
from products.models import Product



# टीप: Payment मॉडेलला वर इम्पोर्ट करू नका, त्यामुळे ImportError येतो.

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
# Buy Now
# ======================
def buy_now(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    return redirect('payments:buy_product', pk=product.id)