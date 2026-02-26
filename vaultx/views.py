import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Count, Q, F
from payments.models import Payment

# ==========================================
# VaultX Dashboard View (FIXED GROUPING)
# ==========================================
def vaultx_home(request):
    session_id = request.session.session_key
    session_email = request.session.get('customer_email')
    user_email = request.user.email if request.user.is_authenticated else session_email

    # 1. Fetch all successful payments for the user
    # Filter mhatvacha ahe jyamule ha count fakt ya user purtach maryadit rahil
    payments_qs = Payment.objects.filter(
        Q(session_id=session_id) | Q(email=user_email),
        status="SUCCESS",
        is_deleted_by_user=False
    ).select_related('product')

    # 2. FIX: Purchase Count Logic
    # .order_by() empty kelyamule Django 'id' nusar group-by na karta 
    # fakt 'product_id' nusar grouping karel.
    purchase_counts = payments_qs.order_by().values('product_id').annotate(total=Count('id'))
    counts_dict = {item['product_id']: item['total'] for item in purchase_counts}

    final_items = {}
    unique_p_ids = counts_dict.keys() # Sidha counts_dict madhle keys vapra

    # Search for latest records (sorting apply kara)
    sorted_payments = payments_qs.order_by('-id')

    for p_id in unique_p_ids:
        # Search for an active payment (where downloads are remaining)
        active_p = sorted_payments.filter(
            product_id=p_id, 
            download_used__lt=F('download_limit'),
            is_active=True
        ).first()

        # If no active payment exists, take the latest expired payment
        display_payment = active_p if active_p else sorted_payments.filter(product_id=p_id).first()
        
        if display_payment:
            # File Existence Check
            product = display_payment.product
            display_payment.file_exists = bool(product.file and os.path.exists(product.file.path))

            # Add correct purchase_count from counts_dict
            display_payment.purchase_count = counts_dict.get(p_id, 1)
            final_items[p_id] = display_payment

    context = {
        "payments": list(final_items.values()),
        "customer_name": request.user.username if request.user.is_authenticated else "Premium Member",
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