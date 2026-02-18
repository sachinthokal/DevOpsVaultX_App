from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q, F
from payments.models import Payment  # तुमचा मॉडेल पाथ तपासा

def vaultx_home(request):
    # १. युजर ओळख पटवणे (Session/Email)
    if not request.session.session_key:
        request.session.create()
        
    session_id = request.session.session_key
    session_email = request.session.get('customer_email')
    user_email = request.user.email if request.user.is_authenticated else session_email

    # २. फक्त यशस्वी (SUCCESS) आणि युजरने डिलीट न केलेली पेमेंट्स मिळवा
    payments_qs = Payment.objects.filter(
        Q(session_id=session_id) | Q(email=user_email),
        status="SUCCESS",
        is_deleted_by_user=False
    ).order_by('-id')

    # ३. स्मार्ट रिसेट लॉजिक (प्रॉडक्ट वाईज क्रेडिट्स तपासणे)
    final_items = {}
    
    # सर्व युनिक प्रॉडक्ट आयडी मिळवा जे युजरने खरेदी केले आहेत
    unique_p_ids = payments_qs.values_list('product_id', flat=True).distinct()

    for p_id in unique_p_ids:
        # आधी तपासा: या प्रॉडक्टसाठी क्रेडिट्स शिल्लक असलेले (Active) पेमेंट आहे का?
        # येथे आपण retry_count ऐवजी download_used वापरत आहोत
        active_p = payments_qs.filter(
            product_id=p_id, 
            download_used__lt=F('download_limit'),
            is_active=True
        ).first()

        if active_p:
            # जर नवीन/Active खरेदी असेल, तर तीच डॅशबोर्डवर दिसेल
            final_items[p_id] = active_p
        else:
            # जर सर्व क्रेडिट्स संपले असतील, तर सर्वात नवीन Expired रेकॉर्ड दाखवा
            final_items[p_id] = payments_qs.filter(product_id=p_id).first()

    # ४. डिस्प्ले नाव सेट करणे
    display_name = "Premium Member"
    if request.user.is_authenticated:
        display_name = request.user.get_full_name() or request.user.username
    elif payments_qs.exists():
        display_name = payments_qs.first().customer_name or "Premium Member"

    context = {
        "payments": list(final_items.values()),
        "customer_email": user_email,
        "customer_name": display_name,
    }
    return render(request, "vaultx/dashboard.html", context)

# ५. कार्ड डिलीट (Hide) करण्याचे फंक्शन
def delete_vault_item(request, payment_id):
    # सुरक्षेसाठी फक्त GET किंवा POST विनंतीवर प्रक्रिया करा
    payment = get_object_or_404(Payment, id=payment_id)
    
    # कार्ड पूर्णपणे डिलीट न करता फक्त डॅशबोर्डवरून लपवा (Hide)
    payment.is_deleted_by_user = True
    payment.save()
    
    return JsonResponse({
        "status": "success", 
        "message": "Item removed from dashboard successfully."
    })