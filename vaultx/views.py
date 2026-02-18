import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q, F
from payments.models import Payment


from django.db.models import Count, Q, F

def vaultx_home(request):
    session_id = request.session.session_key
    session_email = request.session.get('customer_email')
    user_email = request.user.email if request.user.is_authenticated else session_email

    # १. युजरचे सर्व यशस्वी पेमेंट्स मिळवा
    payments_qs = Payment.objects.filter(
        Q(session_id=session_id) | Q(email=user_email),
        status="SUCCESS",
        is_deleted_by_user=False
    ).order_by('-id')

    # २. प्रत्येक प्रॉडक्ट किती वेळा खरेदी केला आहे (Purchase Count) त्याची मोजणी करा
    # हे 'Renewal History' दाखवण्यासाठी लागेल
    purchase_counts = payments_qs.values('product_id').annotate(total=Count('id'))
    counts_dict = {item['product_id']: item['total'] for item in purchase_counts}

    final_items = {}
    unique_p_ids = payments_qs.values_list('product_id', flat=True).distinct()

    for p_id in unique_p_ids:
        # क्युरी सेटमधून ऍक्टिव्ह पेमेंट शोधा (ज्याचे डाउनलोड शिल्लक आहेत)
        active_p = payments_qs.filter(
            product_id=p_id, 
            download_used__lt=F('download_limit'),
            is_active=True
        ).first()

        # जर ऍक्टिव्ह नसेल तर लेटेस्ट एक्सपायर झालेलं पेमेंट घ्या
        display_payment = active_p if active_p else payments_qs.filter(product_id=p_id).first()
        
        if display_payment:
            # टेम्पलेटमध्ये वापरण्यासाठी purchase_count डेटा जोडा
            display_payment.purchase_count = counts_dict.get(p_id, 1)
            final_items[p_id] = display_payment

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