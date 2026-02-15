# db_monitor/admin.py
from django.contrib import admin
from django.template.response import TemplateResponse
from django.db.models import Count, Sum, F
from django.utils import timezone
from .models import DBSize, PaymentSummary
from .utils.db_size import generate_db_size_report
from payments.models import Payment  # Payment model

@admin.register(DBSize)
class DBSizeAdmin(admin.ModelAdmin):
    change_list_template = "admin/db_size.html"

    def get_queryset(self, request):
        return super().get_queryset(request).none()

    def changelist_view(self, request, extra_context=None):
        report = generate_db_size_report()
        context = {
            **admin.site.each_context(request),
            "title": "DB Size Report",
            "report": report,
            "opts": self.model._meta,
        }
        return TemplateResponse(request, "admin/db_size.html", context)


@admin.register(PaymentSummary)
class PaymentSummaryAdmin(admin.ModelAdmin):
    change_list_template = "admin/payment_summary.html"

    def get_queryset(self, request):
        return super().get_queryset(request).none()

    def changelist_view(self, request, extra_context=None):
        # 1. Product-wise detailed analytics (Unique vs Total)
        # retry_count + 1 (original entry) = Total Hits
        product_stats = Payment.objects.filter(status="SUCCESS").values(
            'product__title'
        ).annotate(
            unique_users=Count('session_id', distinct=True),  # Unique Session Count
            total_downloads=Sum('retry_count') + Count('id'), # Total Clicks
            total_revenue=Sum('amount') / 100  # Paise to Rupees
        ).order_by('-total_downloads')

        # 2. Daily Monitor
        today = timezone.now().date()
        today_count = Payment.objects.filter(status="SUCCESS", created_at__date=today).count()

        # 3. Overall Breakdown
        free_count = Payment.objects.filter(status="SUCCESS", amount=0).count()
        paid_count = Payment.objects.filter(status="SUCCESS", amount__gt=0).count()
        
        # 4. Total Platform Revenue
        total_platform_revenue = Payment.objects.filter(status="SUCCESS").aggregate(
            total=Sum('amount'))['total'] or 0
        total_platform_revenue /= 100

        context = {
            **admin.site.each_context(request), # Sidebar/Header context sathi
            "title": "Product Download Summary",
            "product_stats": product_stats,
            "today_count": today_count,
            "free_count": free_count,
            "paid_count": paid_count,
            "total_revenue": total_platform_revenue,
            "today_date": timezone.now(),
            "opts": self.model._meta,
        }
        return TemplateResponse(request, "admin/payment_summary.html", context)