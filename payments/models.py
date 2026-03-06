from django.db import models
from django.contrib.auth.models import User
from products.models import Product
import uuid

class Payment(models.Model):

    secure_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    STATUS_CHOICES = (
        ("INIT", "INIT"),
        ("FAILED", "FAILED"),
        ("SUCCESS", "SUCCESS"),
    )
    # Core Relations
    # ForeignKey to User added to fix the 'unexpected keyword argument user' error
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="payments")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="payments")
    
    # Customer Info
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(db_index=True, blank=True, null=True)
    session_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)

    # Razorpay Details
    razorpay_order_id = models.CharField(max_length=100, db_index=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    # Transaction Info
    amount = models.PositiveIntegerField(help_text="Amount in paise")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="INIT", db_index=True)
    paid = models.BooleanField(default=False)

    # Usage Credits
    download_limit = models.PositiveSmallIntegerField(default=5)
    download_used = models.PositiveSmallIntegerField(default=0)
    
    # Flags
    is_active = models.BooleanField(default=True)
    is_renewal = models.BooleanField(default=False)
    is_deleted_by_user = models.BooleanField(default=False, help_text="Hide from UI")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'devopsvaultx_payments'
        verbose_name = "DevOpsVaultX Payment"
        verbose_name_plural = "DevOpsVaultX Payments"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.title} | {self.email or 'Guest'} | {self.status}"

    @property
    def remaining_credits(self):
        return max(0, self.download_limit - self.download_used)