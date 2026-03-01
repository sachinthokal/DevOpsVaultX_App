from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # List view settings
    list_per_page = 20
    ordering = ['-created_at']
    
    # Search fields (User cha username pan search karta yeil)
    search_fields = ('customer_name', 'email', 'razorpay_order_id', 'product__title', 'user__username')

    # Columns jo tula admin panel madhe distil
    list_display = (
        'id', 'status_badge', 'user_link', 'product_name', 
        'customer_email', 'price_display', 'credits_status', 'created_at'
    )
    
    # Filters (Side panel madhun filter karnyathi)
    list_filter = ('status', 'paid', 'is_active', 'product', 'created_at')

    # Non-editable fields
    readonly_fields = ('created_at', 'updated_at', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')

    # Form layout (Edit page sathi)
    fieldsets = (
        ('👤 CUSTOMER & IDENTITY', {
            'fields': (('user', 'session_id'), ('customer_name', 'email'))
        }),
        ('💰 TRANSACTION DETAILS', {
            'fields': (('product', 'amount'), ('status', 'paid', 'is_renewal'))
        }),
        ('📊 DOWNLOAD USAGE', {
            'fields': (('download_limit', 'download_used'), ('is_active', 'is_deleted_by_user'))
        }),
        ('🔐 GATEWAY METADATA', {
            'classes': ('collapse',), 
            'fields': ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
        }),
    )

    # --- Custom Column Methods ---

    @admin.display(description="Price")
    def price_display(self, obj):
        if obj.amount == 0:
            return format_html('<span style="color: #27ae60; font-weight: bold;">FREE</span>')
        rupees = obj.amount / 100.0
        return f"₹ {rupees:,.2f}"

    @admin.display(description="Status")
    def status_badge(self, obj):
        colors = {
            'SUCCESS': '#2ed573', # Green
            'FAILED': '#ff4757',  # Red
            'INIT': '#ffa502',    # Orange
        }
        color = colors.get(obj.status, '#747d8c')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: bold;">{}</span>',
            color, obj.status
        )

    @admin.display(description="User")
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}" style="font-weight:bold;">{}</a>', url, obj.user.username)
        return format_html('<span style="color: #95a5a6;">Guest</span>')

    @admin.display(description="Product")
    def product_name(self, obj):
        return obj.product.title

    @admin.display(description="Email")
    def customer_email(self, obj):
        return obj.email or "N/A"

    @admin.display(description="Credits")
    def credits_status(self, obj):
        color = "#2ecc71" if obj.remaining_credits > 0 else "#e74c3c"
        return format_html(
            '<b>{}</b> / {} <small style="color: {};">({} left)</small>',
            obj.download_used, obj.download_limit, color, obj.remaining_credits
        )

    # Admin la saglyanche records dakhvnyasathi
    def get_queryset(self, request):
        return super().get_queryset(request)