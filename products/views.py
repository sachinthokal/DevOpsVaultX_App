import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, JsonResponse
from django.contrib import messages
from django.db.models import Q, F
from db_monitor import models
from payments.models import Payment
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
# Secure File Download (Final Fixed Credit-Based Logic)
# ======================
def download_file(request, pk):
    # १. Session आणि User Details ओळखणे
    if not request.session.session_key:
        request.session.create()
    
    session_id = request.session.session_key
    session_email = request.session.get('customer_email')
    user_email = request.user.email if request.user.is_authenticated else None
    
    # force_download फ्लॅग (जेव्हा ब्राउझर प्रत्यक्ष फाईल मागतो)
    is_forcing = request.GET.get('force_download') == '1'

    # २. सर्च क्वेरी (Email किंवा Session वरून ओळख पटवणे)
    search_query = Q(session_id=session_id)
    if session_email:
        search_query |= Q(email=session_email)
    if user_email:
        search_query |= Q(email=user_email)

    # ३. पेमेंट शोधणे (STRICT CREDIT LOGIC)
    # येथे 'F' वापरताना 'models.F' ऐवजी डायरेक्ट 'F' वापरला आहे कारण वरून तो इम्पोर्ट केलाय.
    payment = Payment.objects.filter(
        product_id=pk, 
        status="SUCCESS",
        is_active=True,
        download_used__lt=F('download_limit') # Credit शिल्लक आहेत का?
    ).filter(search_query).order_by('-id').first()

    # ४. जर Active/Credit शिल्लक असलेले पेमेंट नसेल, तर शेवटचे Expired पेमेंट शोधा
    if not payment:
        payment = Payment.objects.filter(
            product_id=pk, 
            status="SUCCESS"
        ).filter(search_query).order_by('-id').first()

    # ५. जर डेटाबेसमध्ये या ईमेल/सेशनसाठी पेमेंटच नसेल
    if not payment:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"status": "error", "message": "Access Denied. खरेदी सापडली नाही."}, status=403)
        return redirect('products:detail', pk=pk)

    # ६. क्रेडिट्स आणि लिमिट तपासणे
    if not is_forcing:
        # जर सापडलेल्या रेकॉर्डचे क्रेडिट्स संपले असतील (5/5 झाले असेल)
        if payment.download_used >= payment.download_limit:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    "status": "error", 
                    "message": "या खरेदीचे डाऊनलोड क्रेडिट्स संपले आहेत. नवीन डाऊनलोडसाठी पुन्हा खरेदी करा."
                }, status=400)
            return redirect('vaultx:index')

        # क्रेडिट अपडेट करा (retry_count ला हात न लावता)
        payment.download_used += 1
        
        # जर लिमिट पूर्ण झाले असेल तर तो विशिष्ट ॲक्सेस बंद करा
        if payment.download_used >= payment.download_limit:
            payment.is_active = False
            
        payment.save()

    # ७. प्रॉडक्ट आणि फाईल पाथ तपासणे
    product = get_object_or_404(Product, pk=pk)
    if not product.file or not os.path.exists(product.file.path):
        return JsonResponse({"status": "error", "message": "फाईल सर्व्हरवर उपलब्ध नाही."}, status=404)

    # ८. AJAX विनंती असल्यास डाऊनलोड URL पाठवणे
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and not is_forcing:
        return JsonResponse({
            "status": "success",
            "credits_used": payment.download_used,
            "total_limit": payment.download_limit,
            "download_url": f"/products/{pk}/download/?force_download=1"
        })

    # ९. प्रत्यक्ष फाईल ट्रान्सफर (Binary Download)
    try:
        response = FileResponse(open(product.file.path, "rb"), as_attachment=True)
        filename = os.path.basename(product.file.path)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Server Error: {str(e)}"}, status=500)