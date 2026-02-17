import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, JsonResponse
from django.contrib import messages
from django.db.models import Q
from .models import Product

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
# Secure File Download (Final & Clean Fix)
# ======================
def download_file(request, pk):
    # Circular Import टाळण्यासाठी local import
    from payments.models import Payment
    import os

    # १. Session आणि User Details
    if not request.session.session_key:
        request.session.create()
    
    session_id = request.session.session_key
    session_email = request.session.get('customer_email')
    user_email = request.user.email if request.user.is_authenticated else None
    
    # force_download फ्लॅग (हा JavaScript मधून येतो)
    is_forcing = request.GET.get('force_download') == '1'

    # २. पेमेंट शोधणे (Updated Query)
    search_query = Q(session_id=session_id)
    if session_email:
        search_query |= Q(email=session_email)
    if user_email:
        search_query |= Q(email=user_email)

    payment = Payment.objects.filter(
        product_id=pk, 
        status="SUCCESS"
    ).filter(search_query).first()

    # ३. पेमेंट नसेल तर ॲक्सेस नाकारा
    if not payment:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"status": "error", "message": "Access Denied. पेमेंट सापडले नाही."}, status=403)
        messages.error(request, "कृपया हे उत्पादन आधी खरेदी करा.")
        return redirect('products:detail', pk=pk)

    # ४. डाउनलोड लिमिट चेक (फक्त AJAX कॉलमध्ये काऊंट वाढवायचा)
    if not is_forcing:
        if payment.retry_count >= 5:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"status": "error", "message": "Limit reached!"}, status=400)
            return redirect('vaultx:index')

        # ५. काउंट वाढवा आणि सेव्ह करा
        payment.retry_count += 1
        # जर ५ झाला तर ॲक्सेस बंद करण्यासाठी 'paid' फ्लॅग False करू शकतोस (Optional)
        # if payment.retry_count >= 5: payment.paid = False 
        payment.save()

    # ६. प्रॉडक्ट आणि फाईल पाथ तपासणे
    product = get_object_or_404(Product, pk=pk)
    if not product.file or not os.path.exists(product.file.path):
        return JsonResponse({"status": "error", "message": "फाईल सर्व्हरवर उपलब्ध नाही."}, status=404)

    # ७. AJAX विनंती असल्यास JSON पाठवा (हा UI अपडेट करतो)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and not is_forcing:
        return JsonResponse({
            "status": "success",
            "new_count": payment.retry_count,
            "download_url": f"/products/{pk}/download/?force_download=1" # Hardcoded safe URL
        })

    # ८. प्रत्यक्ष फाईल डाऊनलोड (Binary Response)
    try:
        # FileResponse सुरक्षितपणे पाठवणे
        response = FileResponse(open(product.file.path, "rb"), as_attachment=True)
        filename = os.path.basename(product.file.path)
        # फाईल नावातील स्पेस काढून टाकणे अधिक सुरक्षित असते
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        # जर फाईल उघडताना एरर आला तर
        return JsonResponse({"status": "error", "message": f"Server Error: {str(e)}"}, status=500)