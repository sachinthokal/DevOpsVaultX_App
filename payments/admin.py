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
        'customer_name',       # ✅ नवीन कॉलम अ‍ॅड केला
        'email',               # ✅ नवीन कॉलम अ‍ॅड केला
        'razorpay_order_id',
        'razorpay_payment_id',
        'amount',
        'status',
        'paid',
        'retry_count',
        'created_at',
    )

    # Filters in the sidebar
    list_filter = ('status', 'paid', 'created_at')

    # Search box fields - आता तुम्ही ईमेल आणि नावाने सुद्धा सर्च करू शकता
    search_fields = (
        'razorpay_order_id', 
        'razorpay_payment_id', 
        'product__title',
        'customer_name',       # ✅ सर्चमध्ये अ‍ॅड केले
        'email'                # ✅ सर्चमध्ये अ‍ॅड केले
    )

    # Read-only fields
    readonly_fields = ('created_at', 'updated_at')