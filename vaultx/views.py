import os
from django.shortcuts import redirect, render, get_object_or_404
from django.http import FileResponse, HttpResponseForbidden, JsonResponse
from payments.models import Payment # Tumcha model path check kara
from django.db.models import Count, F, Q

from products.models import Product  # Q import kela aahe

def vaultx_home(request):
    if not request.user.is_authenticated:
        return render(request, "vaultx/dashboard.html", {"payments": [], "is_logged_in": False})

    # 1. Purna History fetch kara (Latest ID first sathi '-id' vapra)
    all_successful_payments = Payment.objects.filter(
        Q(user=request.user) | Q(email=request.user.email),
        Q(status__in=["SUCCESS", "COMPLETED"]) | Q(amount=0)
    ).order_by('-id')

    # Product wise total purchase count
    purchase_counts = all_successful_payments.values('product_id').annotate(total=Count('id'))
    counts_dict = {item['product_id']: item['total'] for item in purchase_counts}

    # 2. Display Logic: Non-deleted payments
    display_qs = all_successful_payments.filter(is_deleted_by_user=False).select_related('product')

    final_items = {}
    
    # Unique product IDs chi list
    product_ids = display_qs.values_list('product_id', flat=True).distinct()

    for p_id in product_ids:
        # Ya product che sagle records ghy
        product_records = display_qs.filter(product_id=p_id)

        # ✅ CRITICAL FIX: Pahalanda te record shodha jyache CREDITS BAKI aahet
        # Filter madhe 'is_active=True' ani 'download_used < limit' aslela record priority var ghy
        display_payment = product_records.filter(
            download_used__lt=F('download_limit'),
            is_active=True
        ).first()

        # Jar ek pan active record nasel, tarach latest expired record dakhva
        if not display_payment:
            display_payment = product_records.first()

        if display_payment:
            product = display_payment.product
            # File check logic
            display_payment.file_exists = bool(product.file and os.path.exists(product.file.path))
            # History count set kara
            display_payment.purchase_count = counts_dict.get(p_id, 1)
            final_items[p_id] = display_payment

    # Dashboard var sorting (Latest active purchase var yaava)
    sorted_payments = sorted(
        final_items.values(),
        key=lambda x: x.id, 
        reverse=True
    )

    context = {
        "payments": sorted_payments,
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
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden, FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.db.models import F
import os

@login_required
def download_file(request, token, product_id):

    # 1️⃣ Product fetch
    product = get_object_or_404(Product, pk=product_id)

    # 2️⃣ Payment fetch using secure_token
    payment = get_object_or_404(
        Payment,
        secure_token=token,
        product_id=product_id,
        user=request.user
    )

    # 3️⃣ payment status validation
    if payment.status not in ["SUCCESS", "COMPLETED"] and payment.amount != 0:
        messages.error(request, "Invalid payment status.")
        return redirect("vaultx:index")

    # 4️⃣ File existence check
    if not product.file or not os.path.exists(product.file.path):
        messages.error(request, "File not available.")
        return redirect("vaultx:index")

    # ======================
    # AJAX CREDIT CHECK
    # ======================
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':

        if payment.download_used >= payment.download_limit:
            return JsonResponse({
                "status": "error",
                "message": "Download limit reached."
            }, status=400)

        # 🔐 store authorization in session
        request.session['download_auth'] = str(payment.secure_token)

        return JsonResponse({
            "status": "success",
            "download_url": f"/vaultx/download/{token}/{product_id}/?download=1"
        })

    # ======================
    # ACTUAL FILE DOWNLOAD
    # ======================
    if request.GET.get("download") == "1":

        # 🔐 verify session authorization
        session_token = request.session.get("download_auth")

        if not session_token or session_token != str(payment.secure_token):
            messages.error(request, "Unauthorized download attempt.")
            return redirect("vaultx:index")

        # remove session after use
        del request.session["download_auth"]

        # re-check limit
        if payment.download_used >= payment.download_limit:
            messages.error(request, "Download limit reached. Please renew the asset.")
            return redirect("vaultx:index")

        try:

            # safe increment
            Payment.objects.filter(id=payment.id).update(
                download_used=F('download_used') + 1
            )

            payment.refresh_from_db()

            if payment.download_used >= payment.download_limit:
                payment.is_active = False
                payment.save(update_fields=["is_active"])

            response = FileResponse(
                open(product.file.path, "rb"),
                as_attachment=True
            )

            response["Content-Disposition"] = f'attachment; filename="{os.path.basename(product.file.path)}"'

            return response

        except Exception:
            return HttpResponseForbidden("File access error")

    return HttpResponseForbidden("Invalid request")