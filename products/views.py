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

# ======================
# Payment Success Callback
# ======================
def confirm_payment(request, pk):
    request.session[f'paid_{pk}'] = True
    return redirect('products:download_file', pk=pk)

# ======================
# Secure File Download (Optimized & Fixed)
# ======================
def download_file(request, pk):
    if not request.session.session_key:
        request.session.create()
    
    session_id = request.session.session_key
    session_email = request.session.get('customer_email')
    user_email = request.user.email if request.user.is_authenticated else None
    
    # १. ओळख पटवण्यासाठी सर्च क्वेरी
    search_query = Q(session_id=session_id)
    if session_email: search_query |= Q(email=session_email)
    if user_email: search_query |= Q(email=user_email)

    is_forcing = request.GET.get('force_download') == '1'

    # २. AJAX विनंती: क्रेडिट चेक आणि वजा करणे
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and not is_forcing:
        payment = Payment.objects.filter(
            search_query,
            product_id=pk, 
            status="SUCCESS",
            is_active=True,
            download_used__lt=F('download_limit')
        ).order_by('-id').first()

        if not payment:
            return JsonResponse({
                "status": "error", 
                "message": "डाउनलोड क्रेडिट्स संपले आहेत किंवा खरेदी सापडली नाही."
            }, status=400)

        # क्रेडिट वजा करा
        payment.download_used += 1
        if payment.download_used >= payment.download_limit:
            payment.is_active = False
        payment.save()

        return JsonResponse({
            "status": "success",
            "download_url": f"/products/{pk}/download/?force_download=1"
        })

    # ३. Direct Download (force_download=1): फक्त फाईल डिलिव्हरी
    if is_forcing:
        has_paid = Payment.objects.filter(
            search_query,
            product_id=pk,
            status="SUCCESS"
        ).exists()

        if not has_paid:
            messages.error(request, "Access Denied: Payment not verified.")
            return redirect('vaultx:index') # Tuzya dashboard cha path tak

        product = get_object_or_404(Product, pk=pk)

        # --- FIX: File Exist Check ---
        if not product.file:
            messages.error(request, "Product Expired: No file path found in database.")
            
        
        if not os.path.exists(product.file.path):
            messages.error(request, "Product Expired: File has been removed.")
            return redirect('vaultx:index')
        # -----------------------------

        try:
            response = FileResponse(open(product.file.path, "rb"), as_attachment=True)
            filename = os.path.basename(product.file.path)
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            messages.error(request, f"Server Error: {str(e)}")
            return redirect('vaultx:index')

    return redirect('products:detail', pk=pk)