from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    ordering = ['-created_at']
    list_display = ('product', 'razorpay_order_id', 'paid', 'created_at')
