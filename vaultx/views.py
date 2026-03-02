import os
from django.shortcuts import redirect, render, get_object_or_404
from django.http import FileResponse, HttpResponseForbidden, JsonResponse
from payments.models import Payment # Tumcha model path check kara
from django.db.models import Count, F, Q

from products.models import Product  # Q import kela aahe

def vaultx_home(request):
    if not request.user.is_authenticated:
        return render(request, "vaultx/dashboard.html", {"payments": [], "is_logged_in": False})

    # 1. Purna History: Count sathi sagle यशस्वी payments ghya (Deleted pan dakhva count madhe)
    all_successful_payments = Payment.objects.filter(
        Q(user=request.user) | Q(email=request.user.email),
        Q(status="SUCCESS") | Q(status="COMPLETED") | Q(amount=0)
    )

    # Product wise count kadha
    purchase_counts = all_successful_payments.values('product_id').annotate(total=Count('id'))
    counts_dict = {item['product_id']: item['total'] for item in purchase_counts}

    # 2. Display Logic: Fakt te payments dakhva je user ne delete nahi kele
    display_qs = all_successful_payments.filter(is_deleted_by_user=False).select_related('product')

    final_items = {}
    
    # Pratyek product sathi ek best record nivda
    for p_id, total_count in counts_dict.items():
        # Jar user ne sagale records delete kele astil tar to product dakhvu naka
        active_display = display_qs.filter(product_id=p_id).order_by('-id')
        
        if not active_display.exists():
            continue

        # Try to find an active one (not fully used)
        display_payment = active_display.filter(
            download_used__lt=F('download_limit'),
            is_active=True
        ).first()

        # Jar active nasel tar latest available record ghya
        if not display_payment:
            display_payment = active_display.first()

        if display_payment:
            product = display_payment.product
            # File existence check
            display_payment.file_exists = bool(product.file and os.path.exists(product.file.path))
            # FIX: Purna history cha count dakhva
            display_payment.purchase_count = total_count
            final_items[p_id] = display_payment

    context = {
        "payments": list(final_items.values()),
        "is_logged_in": True,
        "customer_name": request.user.username,
    }
    return render(request, "vaultx/dashboard.html", context)


# ==========================================
# Delete Item (Security Fixed)
# ==========================================
def delete_vault_item(request, payment_id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.user.is_authenticated:
        # Security: Fakt swatahchech payment delete karta yetil
        payment = get_object_or_404(Payment, id=payment_id, email=request.user.email)
        payment.is_deleted_by_user = True
        payment.save()
        return JsonResponse({"status": "success"})
    
    return JsonResponse({"status": "error", "message": "Unauthorized"}, status=400)

# ==========================================
# Receipt Download Fix
# ==========================================
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from payments.models import Payment  

@login_required
def generate_receipt_pdf(request, order_id):
    # Payment fetch kara
    payment = get_object_or_404(Payment, razorpay_order_id=order_id)
    
    # Dynamic Product Details ghy (Jar Payment model madhe product FK asel tar)
    product = payment.product 
    
    # Jar features list madhe pahije astil tar tyala split kara (समजा database madhe comma-separated aahet)
    # Nasel tar ek default list set kara
    features = [
        "Lifetime Full Access to " + product.title,
        "Premium Documentation & PDF Guides",
        "Source Code & Project Assets",
        "24/7 Priority Support Access",
        "Future Updates Included"
    ]

    context = {
        'order_id': payment.razorpay_order_id,
        'payment_id': payment.razorpay_payment_id,
        'product_id': payment.product_id,
        'user_fullname': payment.customer_name or payment.user.get_full_name() or payment.user.username,
        'user_email': payment.email or payment.user.email,
        'purchase_date': payment.created_at.strftime("%d %b %Y"),
        'amount': "{:.2f}".format(payment.amount / 100),
        'product_title': product.title, # Dynamic Title
        'product_features': features,    # Dynamic Features List
    }
    
    return render(request, 'vaultx/receipt_print.html', context)

# ======================
# 3. SECURE DOWNLOAD (Credit Logic)
# ======================
def download_file(request, product_id, payment_id):
    # १. फाईल आणि पेमेंट रेकॉर्ड मिळवा
    product = get_object_or_404(Product, pk=product_id)
    payment = get_object_or_404(Payment, id=payment_id, email=request.user.email)

    is_forcing = request.GET.get('force_download') == '1'

    # २. AJAX Request: क्रेडिट चेक आणि वजावट
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and not is_forcing:
        
        # क्रेडिट शिल्लक आहे का ते तपासा
        if payment.download_used >= payment.download_limit:
            return JsonResponse({"status": "error", "message": "Download limit reached for this purchase."}, status=400)

        if not product.file or not os.path.exists(product.file.path):
            return JsonResponse({"status": "error", "message": "File not found on server."}, status=404)

        # क्रेडिट कमी करा
        payment.download_used += 1
        if payment.download_used >= payment.download_limit:
            payment.is_active = False
        payment.save()

        # परतीची URL (ह्याच फंक्शनला पुन्हा कॉल करेल पण force_download=1 सह)
        download_url = f"/vaultx/download/{product_id}/{payment_id}/?force_download=1"
        return JsonResponse({"status": "success", "download_url": download_url})

    # ३. प्रत्यक्ष फाईल डाउनलोड (जेव्हा force_download=1 असेल)
    if is_forcing:
        try:
            response = FileResponse(open(product.file.path, "rb"), as_attachment=True)
            response["Content-Disposition"] = f'attachment; filename="{os.path.basename(product.file.path)}"'
            return response
        except Exception as e:
            return HttpResponseForbidden("File access error")

    return redirect('vaultx:index')