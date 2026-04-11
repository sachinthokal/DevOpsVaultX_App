from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from products.models import Product


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
# Buy Now (Fixed for Authentication)
# ======================
def buy_now(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    
    # जर युजर लॉगिन नसेल तर पेमेंटवर जाऊ नका
    if not request.user.is_authenticated:
        # Product details page वर परत पाठवा आणि एक सिग्नल द्या (login_trigger)
        messages.warning(request, "Please login to purchase this product.")        
        base_url = reverse('products:details', args=[product.id])
        return redirect(f"{base_url}?login_trigger=true")
    
    # युजर लॉगिन असेल तरच पेमेंट प्रोसेस सुरू करा
    return redirect('payments:buy_product', pk=product.id)