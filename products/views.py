import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, HttpResponseForbidden
from django.urls import reverse
from django.contrib import messages  # मेसेज दाखवण्यासाठी
from payments.models import Payment
from .models import Product


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
# Secure File Download (Final Optimized Fix)
# ======================
# ======================
# Secure File Download (Fix: 5th Download Allowed)
# ======================
def download_file(request, pk):
    session_id = request.session.session_key
    session_key = f"paid_{pk}"

    # १. डेटाबेसमध्ये पेमेंट तपासा
    payment = Payment.objects.filter(
        product_id=pk, 
        status="SUCCESS", 
        paid=True,
        session_id=session_id
    ).first()

    # २. जर पेमेंट सापडले, तर आधी लिमिट तपासा
    if payment:
        # ✅ बदल: जोपर्यंत काउंट ५ पेक्षा कमी आहे तोपर्यंत डाऊनलोड करू द्या
        # जर काउंट आधीच ५ झाला असेल, तरच बाहेर काढा
        if payment.retry_count >= 5:
            payment.paid = False
            payment.save()
            messages.warning(request, "Your download limit (5 times) has been reached. Please purchase again for access.")
            return redirect('products:detail', pk=pk)
            
    # ३. जर पेमेंट नसेल आणि सेशनमध्ये 'Free Access' नसेल, तर रिडरेक्ट करा
    elif not request.session.get(session_key):
        messages.error(request, "Access Denied. Please purchase the product first.")
        return redirect('products:detail', pk=pk)

    # ४. प्रॉडक्ट आणि फाईलची उपलब्धता तपासा
    product = get_object_or_404(Product, pk=pk, is_active=True)
    
    if not product.file or not os.path.exists(product.file.path):
        messages.error(request, "Resource file is currently unavailable on server.")
        return redirect('products:detail', pk=pk)

    file_path = product.file.path

    # ५. डाऊनलोड काउंट वाढवा
    if payment:
        # काउंट वाढवण्यापूर्वी तो ५ आहे का ते पुन्हा एकदा खात्री करा (Double Check)
        if payment.retry_count < 5:
            payment.retry_count += 1
            
            # ५ वा डाऊनलोड झाला असेल तरच 'paid' घालवा
            if payment.retry_count >= 5:
                payment.paid = False
            
            payment.save()
        else:
            # सुरक्षिततेसाठी जर चुकून काउंट वाढला असेल तर इथूनच रिडरेक्ट करा
            return redirect('products:detail', pk=pk)

    # ६. FileResponse पाठवा
    try:
        file_handle = open(file_path, "rb")
        response = FileResponse(file_handle, as_attachment=True)
        original_filename = os.path.basename(file_path)
        response["Content-Disposition"] = f'attachment; filename="{original_filename}"'
        return response
    except Exception as e:
        messages.error(request, f"Download failed: {str(e)}")
        return redirect('products:detail', pk=pk)

# ======================
# Payment Result Page
# ======================
def payment_result(request, pk):
    session_key = f"paid_{pk}"
    product = get_object_or_404(Product, pk=pk, is_active=True)

    # 1. Check kara product Free aahe ka
    is_free = product.price == 0

    # 2. Database check (Paid products sathi)
    db_paid = Payment.objects.filter(product=product, status="SUCCESS", paid=True).exists()

    # 3. Success condition: Jar Free asel OR Session madhe entry asel OR DB madhe entry asel
    if is_free or request.session.get(session_key) or db_paid:
        status = "success"
        file_url = reverse("products:download_file", args=[pk])
        # Download access sathi session set kara
        request.session[session_key] = True 
    else:
        status = "failed"
        file_url = None

    return render(request, "products/payment_result.html", {
        "status": status,
        "product": product,
        "file_url": file_url,
        "is_free": product.price == 0, # <--- He add kara
    })