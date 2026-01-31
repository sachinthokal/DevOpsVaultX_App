from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # Default ordering: latest payments first
    ordering = ['-created_at']

    # Fields to show in the admin list view
    list_display = (
        'id',
        'product',
        'razorpay_order_id',
        'razorpay_payment_id',
        'amount',
        'status',
        'paid',
        'retry_count',
        'created_at',
        'updated_at',
    )

    # Filters in the sidebar
    list_filter = ('status', 'paid', 'created_at')

    # Search box fields
    search_fields = ('razorpay_order_id', 'razorpay_payment_id', 'product__title')

    # Read-only fields
    readonly_fields = ('created_at', 'updated_at')
