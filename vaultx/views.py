from django.shortcuts import render
from payments.models import Payment
from django.db.models import Q

def vaultx_home(request):
    if not request.session.session_key:
        request.session.create()
    
    session_id = request.session.session_key
    session_email = request.session.get('customer_email')

    search_query = Q(session_id=session_id)
    if session_email:
        search_query |= Q(email=session_email)
    if request.user.is_authenticated:
        search_query |= Q(email=request.user.email)

    # १. आधी सर्व यशस्वी पेमेंट्सची लिस्ट मिळवा. 
    # '-id' वापरल्यामुळे सर्वात नवीन पेमेंट (Latest Payment) सर्वात वर येईल.
    all_success_payments = Payment.objects.filter(
        search_query,
        status="SUCCESS"
    ).order_by('product_id', '-id')

    # २. मॅन्युअल फिल्टर: प्रत्येक प्रॉडक्टचा फक्त लेटेस्ट रेकॉर्ड पकडणे.
    distinct_payments = {}
    for p in all_success_payments:
        # जर प्रॉडक्ट आयडी आधीच आला नसेल, तर तो 'latest' आहे कारण आपण '-id' ने सॉर्ट केले आहे.
        if p.product_id not in distinct_payments:
            distinct_payments[p.product_id] = p
    
    # डिक्शनरीमधून फक्त व्हॅल्यूजची लिस्ट बनवा
    purchased_payments = list(distinct_payments.values())

    # ३. युजर डिटेल्स लॉजिक
    last_payment = purchased_payments[0] if purchased_payments else None

    if request.user.is_authenticated:
        customer_name = request.user.get_full_name() or request.user.username
        customer_email = request.user.email
    elif last_payment:
        customer_name = last_payment.customer_name or "Guest User"
        customer_email = last_payment.email
    else:
        customer_name = "Guest User"
        customer_email = session_email if session_email else "No Premium Access"

    context = {
        "payments": purchased_payments,
        "customer_name": customer_name,
        "customer_email": customer_email,
    }
    return render(request, "vaultx/dashboard.html", context)