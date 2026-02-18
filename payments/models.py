from django.db import models
from products.models import Product

class Payment(models.Model):
    STATUS_CHOICES = (
        ("INIT", "INIT"),
        ("FAILED", "FAILED"),
        ("SUCCESS", "SUCCESS"),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="payments")
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(db_index=True, blank=True, null=True)
    email_updated = models.BooleanField(default=False, null=True, blank=True)
    email_otp_verified = models.BooleanField(default=False, null=True, blank=True)
    old_email = models.EmailField(max_length=255, blank=True, null=True)

    # Razorpay/Session Details
    razorpay_order_id = models.CharField(max_length=100, db_index=True)
    session_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    amount = models.PositiveIntegerField(help_text="Amount in paise")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="INIT", db_index=True)
    paid = models.BooleanField(default=False)

    # --- नवीन Subscription/Credit Logic ---
    
    # प्रत्येक खरेदीवर किती डाऊनलोड्स द्यायचे (Default 5)
    download_limit = models.PositiveSmallIntegerField(default=5)
    
    # किती डाऊनलोड्स वापरले (हे आपण वाढवत जाऊ)
    download_used = models.PositiveSmallIntegerField(default=0)

    # हे तसेच ठेवा पण आपण लॉजिक मध्ये वापरणार नाही
    retry_count = models.PositiveSmallIntegerField(default=0)

    is_deleted_by_user = models.BooleanField(default=False, help_text="Hide from UI")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'devopsvaultx_payments'
        verbose_name = "DevOpsVaultX Payment"
        verbose_name_plural = "DevOpsVaultX Payments"

    def __str__(self):
        user_info = self.email if self.email else "Guest"
        return f"{self.product.title} | Credits: {self.download_used}/{self.download_limit}"

    @property
    def remaining_credits(self):
        # शिल्लक राहिलेले क्रेडिट्स काढण्यासाठी
        remaining = self.download_limit - self.download_used
        return max(0, remaining)

    @property
    def has_access(self):
        # ॲक्सेस आहे की नाही हे तपासण्यासाठी
        return self.download_used < self.download_limit and self.is_active