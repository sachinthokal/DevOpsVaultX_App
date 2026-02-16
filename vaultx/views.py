from django.shortcuts import render
from payments.models import Payment

# ======================
# 🔐 User Vault
# ======================
def vaultx_home(request):
    # 1. Session ID ensure kara
    if not request.session.session_key:
        request.session.create()
    session_id = request.session.session_key
    
    # 2. Database madhun successful payments chi list kadha
    purchased_payments = Payment.objects.filter(
        session_id=session_id,
        status="SUCCESS",
        retry_count__lt=5 
    ).select_related('product').order_by('-created_at')

    # 3. User Details logic (To avoid AnonymousUser errors)
    # Jar user login asel tar tyache details pratham ghya
    if request.user.is_authenticated:
        customer_name = request.user.get_full_name() or request.user.username
        customer_email = request.user.email
    else:
        # Jar login nasel, tar last payment record check kara
        last_payment = purchased_payments.first()
        if last_payment:
            customer_name = last_payment.customer_name
            customer_email = last_payment.email
        else:
            # First-time user sathi default values
            customer_name = "VAULTX USER"
            customer_email = "Premium Access Pending"

    # 4. Context setup
    context = {
        "payments": purchased_payments,
        "customer_name": customer_name,
        "customer_email": customer_email,
    }

    return render(request, "vaultx/dashboard.html", context)