import csv
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.apps import apps
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from dashboard.models import SystemLog

# ------------------------- AUTH CHECK ---------------------------------
# फक्त Superuser (Owner) लाच प्रवेश मिळावा यासाठी फंक्शन
def is_owner(user):
    return user.is_authenticated and user.is_superuser

# ------------------------- Admin Dashboards ---------------------------------
@login_required
@user_passes_test(is_owner, login_url='home') # जर सुपरयुजर नसेल तर होम पेजला पाठवेल
def admin_dashboard(request):
    # मॉडेल डायनॅमिकली गेट करा
    User = apps.get_model('auth', 'User')
    Payment = apps.get_model('payments', 'Payment')
    InsightsPost = apps.get_model('insights', 'InsightsPost')
    ContactMessage = apps.get_model('pages', 'ContactMessage')
    Product = apps.get_model('products', 'Product')

    now = timezone.now()
    tz = timezone.get_current_timezone()

    # --- विभाग १: LIFETIME STATS ---
    all_payments = Payment.objects.all()
    lifetime_sales = (all_payments.aggregate(total=Sum('amount'))['total'] or 0) / 100
    lifetime_orders = all_payments.count()
    lifetime_users_count = User.objects.all().count()

    # --- विभाग १.१: LIFETIME STATUS BREAKDOWN ---
    lifetime_success = all_payments.filter(status='SUCCESS').count()
    lifetime_failed = all_payments.filter(status='FAILED').count()
    lifetime_pending = all_payments.filter(status__in=['INIT']).count()

    # --- विभाग २: RANGE FILTER LOGIC ---
    range_type = request.GET.get('range', '7days') 
    ranges = {
        '1hr': now - timedelta(hours=1),
        '6hr': now - timedelta(hours=6),
        '1day': now - timedelta(days=1),
        '7days': now - timedelta(days=7),
        '1month': now - timedelta(days=30),
        '1yr': now - timedelta(days=365),
    }
    start_date = ranges.get(range_type, now - timedelta(days=7))

    # --- विभाग ३: PERIODIC STATS ---
    filtered_payments = Payment.objects.filter(created_at__gte=start_date)
    
    periodic_sales_paise = filtered_payments.aggregate(total=Sum('amount'))['total'] or 0
    periodic_sales = periodic_sales_paise / 100 
    periodic_orders = filtered_payments.count()
    periodic_new_users = User.objects.filter(date_joined__gte=start_date).count()

    # CSV Export
    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="DevOpsVault_Sales_{range_type}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Customer', 'Amount', 'Status', 'Timestamp'])
        for p in filtered_payments:
            writer.writerow([p.id, p.customer_name, p.amount, p.status, p.created_at])
        return response

    # --- विभाग ४: ग्राफ डेटा लॉजिक ---
    chart_data = []
    chart_labels = []

    if range_type == '1hr':
        for i in range(6, 0, -1):
            slot_start = now - timedelta(minutes=i*10)
            slot_end = now - timedelta(minutes=(i-1)*10)
            slot_sum = Payment.objects.filter(created_at__range=(slot_start, slot_end)).aggregate(s=Sum('amount'))['s'] or 0
            chart_labels.append(slot_end.astimezone(tz).strftime('%H:%M'))
            chart_data.append(float(slot_sum / 100.0))

    elif range_type == '6hr':
        for i in range(6, 0, -1):
            slot_start = now - timedelta(hours=i)
            slot_end = now - timedelta(hours=i-1)
            slot_sum = Payment.objects.filter(created_at__range=(slot_start, slot_end)).aggregate(s=Sum('amount'))['s'] or 0
            chart_labels.append(slot_end.astimezone(tz).strftime('%I %p'))
            chart_data.append(float(slot_sum / 100.0))

    elif range_type == '1day':
        for i in range(12, 0, -1):
            slot_start = now - timedelta(hours=i*2)
            slot_end = now - timedelta(hours=(i-1)*2)
            slot_sum = Payment.objects.filter(created_at__range=(slot_start, slot_end)).aggregate(s=Sum('amount'))['s'] or 0
            chart_labels.append(slot_end.astimezone(tz).strftime('%H:%M'))
            chart_data.append(float(slot_sum / 100.0))

    else:
        days_to_show = 7 if range_type == '7days' else (30 if range_type == '1month' else 12)
        for i in range(days_to_show - 1, -1, -1):
            target_date = (now - timedelta(days=i)).date()
            daily_sum = Payment.objects.filter(created_at__date=target_date).aggregate(s=Sum('amount'))['s'] or 0
            chart_labels.append(target_date.strftime('%d %b'))
            chart_data.append(float(daily_sum / 100.0))

    # --- विभाग ५: कॉन्टेक्स्ट ---
    context = {
        'selected_range': range_type.upper(),
        'total_sales': "{:,}".format(int(lifetime_sales)),
        'total_orders': lifetime_orders,
        'total_users': lifetime_users_count,
        'lifetime_success': lifetime_success,
        'lifetime_failed': lifetime_failed,
        'lifetime_pending': lifetime_pending,

        'periodic_sales': "{:,}".format(int(periodic_sales)),
        'periodic_orders': periodic_orders,
        'periodic_users': periodic_new_users,
        
        'users': User.objects.all().order_by('-id')[:15],
        'insights': InsightsPost.objects.all().order_by('-id')[:15],
        'messages': ContactMessage.objects.all().order_by('-id')[:15],
        'payments': Payment.objects.all().order_by('-created_at')[:15],
        'products': Product.objects.all()[:15],
        
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'live_events': [
            f"Range: {range_type.upper()} Mode Activated",
            f"Overall Success Rate: {round((lifetime_success/lifetime_orders)*100, 1) if lifetime_orders > 0 else 0}%",
            "Encryption: SSL/TLS Active",
            "System Status: OPTIMAL"
        ],
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


# ------------------------- SYS_LOGS ---------------------------------
@login_required
@user_passes_test(is_owner)
def get_latest_logs(request):
    logs = SystemLog.objects.all().order_by('-created_at')[:20]
    log_data = []
    for log in logs:
        log_data.append({
            'id': log.id,
            'msg': log.message,
            'type': log.log_type,
            'time': log.created_at.strftime("%H:%M:%S")
        })
    return JsonResponse({'logs': log_data})