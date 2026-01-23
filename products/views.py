from django.shortcuts import render, get_object_or_404
from .models import Product

# Home Page View (Featured Products साठी)
def home(request):
    # फक्त तेच प्रॉडक्ट्स आणा जे Active आहेत
    products = Product.objects.filter(is_active=True).order_by('-created_at')[:3] # टॉप ३ प्रॉडक्ट्स
    return render(request, 'home.html', {'products': products})

# Full Products List View
def product_list(request):
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'products/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})