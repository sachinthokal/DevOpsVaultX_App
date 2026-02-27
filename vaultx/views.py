import os
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, F
from payments.models import Payment # Tumcha model path check kara

import os
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, F, Q  # Q import kela aahe
from payments.models import Payment

def vaultx_home(request):
    if not request.user.is_authenticated:
        return render(request, "vaultx/dashboard.html", {"payments": [], "is_logged_in": False})

    # User ID ani Email donhi check karne safe rahte
    payments_qs = Payment.objects.filter(
        Q(user=request.user) | Q(email=request.user.email),
        Q(status="SUCCESS") | Q(status="COMPLETED") | Q(amount=0),
        is_deleted_by_user=False
    ).select_related('product').order_by('-id')

    # Purchase Count Logic
    purchase_counts = payments_qs.values('product_id').annotate(total=Count('id'))
    counts_dict = {item['product_id']: item['total'] for item in purchase_counts}

    final_items = {}
    sorted_payments = payments_qs.order_by('-id')

    for p_id in counts_dict.keys():
        # Active payment check
        active_p = sorted_payments.filter(
            product_id=p_id, 
            download_used__lt=F('download_limit'),
            is_active=True
        ).first()

        # Jar active nasel tar latest record ghya
        display_payment = active_p if active_p else sorted_payments.filter(product_id=p_id).first()
        
        if display_payment:
            product = display_payment.product
            # File existence check
            display_payment.file_exists = bool(product.file and os.path.exists(product.file.path))
            # Purchase count add kara
            display_payment.purchase_count = counts_dict.get(p_id, 1)
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