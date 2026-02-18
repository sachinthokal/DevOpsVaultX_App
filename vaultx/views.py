import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q, F
from payments.models import Payment


def vaultx_home(request):
    session_id = request.session.session_key
    session_email = request.session.get('customer_email')
    user_email = request.user.email if request.user.is_authenticated else session_email

    payments_qs = Payment.objects.filter(
        Q(session_id=session_id) | Q(email=user_email),
        status="SUCCESS",
        is_deleted_by_user=False
    ).order_by('-id')

    final_items = {}
    unique_p_ids = payments_qs.values_list('product_id', flat=True).distinct()

    for p_id in unique_p_ids:
        active_p = payments_qs.filter(
            product_id=p_id, 
            download_used__lt=F('download_limit'),
            is_active=True
        ).first()
        # जर active नसेल तर latest expired दाखवा
        final_items[p_id] = active_p if active_p else payments_qs.filter(product_id=p_id).first()

    context = {
        "payments": list(final_items.values()),
        "customer_name": request.user.username if request.user.is_authenticated else "Premium Member",
    }
    return render(request, "vaultx/dashboard.html", context)

def delete_vault_item(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    payment.is_deleted_by_user = True
    payment.save()
    return JsonResponse({"status": "success"})