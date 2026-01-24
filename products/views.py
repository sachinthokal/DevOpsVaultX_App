from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, HttpResponseForbidden
from .models import Product


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
    """
    Secure download:
    - Payment must be completed
    - File served as attachment
    """
    if not request.session.get(f'paid_{pk}'):
        return HttpResponseForbidden("❌ Payment not completed")

    product = get_object_or_404(Product, pk=pk, is_active=True)

    if not product.file:
        return HttpResponseForbidden("❌ File not available")

    return FileResponse(
        product.file.open('rb'),
        as_attachment=True,
        filename=product.file.name.split('/')[-1]
    )
