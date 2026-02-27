import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Count, Q, F
from payments.models import Payment

from django.db.models import Q, Count, F
import os

# ==========================================
# VaultX Dashboard View (ONLY LOGGED-IN USERS)
# ==========================================
def vaultx_home(request):
    # 1. Check if user is authenticated
    if not request.user.is_authenticated:
        # Jar user login nasel tar empty context pathva
        return render(request, "vaultx/dashboard.html", {"payments": [], "customer_name": "Guest"})

    user_email = request.user.email
    
    # 2. Fetch successful payments ONLY for the logged-in user
    payments_qs = Payment.objects.filter(
        email=user_email,
        status="SUCCESS",
        is_deleted_by_user=False
    ).select_related('product')

    # 3. Purchase Count Logic
    purchase_counts = payments_qs.order_by().values('product_id').annotate(total=Count('id'))
    counts_dict = {item['product_id']: item['total'] for item in purchase_counts}

    final_items = {}
    unique_p_ids = counts_dict.keys()

    # Latest records sathi sorting
    sorted_payments = payments_qs.order_by('-id')

    for p_id in unique_p_ids:
        # Active payment check (remaining downloads)
        active_p = sorted_payments.filter(
            product_id=p_id, 
            download_used__lt=F('download_limit'),
            is_active=True
        ).first()

        # Jar active nasel tar latest expired record ghya
        display_payment = active_p if active_p else sorted_payments.filter(product_id=p_id).first()
        
        if display_payment:
            # File Existence Check
            product = display_payment.product
            display_payment.file_exists = bool(product.file and os.path.exists(product.file.path))

            # Add purchase_count
            display_payment.purchase_count = counts_dict.get(p_id, 1)
            final_items[p_id] = display_payment

    context = {
        "payments": list(final_items.values()),
        "customer_name": request.user.username,
    }
    return render(request, "vaultx/dashboard.html", context)


# ==========================================
# Delete Item from Vault
# ==========================================
def delete_vault_item(request, payment_id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        payment = get_object_or_404(Payment, id=payment_id)
        payment.is_deleted_by_user = True
        payment.save()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)