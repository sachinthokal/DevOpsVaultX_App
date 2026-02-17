from django.db import models
from products.models import Product

class Payment(models.Model):

    STATUS_CHOICES = (
        ("INIT", "INIT"),
        ("FAILED", "FAILED"),
        ("SUCCESS", "SUCCESS"),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    # Guest User चा डेटा साठवण्यासाठी
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(db_index=True, blank=True, null=True)

    # ईमेल अपडेट ट्रॅकिंग
    email_updated = models.BooleanField(default=False, null=True, blank=True)

    # email_otp_verified default False ठेवले आहे कारण OTP व्हेरिफिकेशन नंतरच ते True होईल
    email_otp_verified = models.BooleanField(default=False, null=True, blank=True)
    
    # 🔥 जुना ईमेल साठवण्यासाठी नवीन कॉलम (हा अ‍ॅड केला आहे)
    old_email = models.EmailField(max_length=255, blank=True, null=True)

    # Razorpay Order ID
    razorpay_order_id = models.CharField(
        max_length=100,
        db_index=True
    )

    # Unique users ट्रॅक करण्यासाठी
    session_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        db_index=True
    )

    razorpay_payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True
    )

    razorpay_signature = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    amount = models.PositiveIntegerField(
        help_text="Amount in paise"
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="INIT",
        db_index=True
    )

    paid = models.BooleanField(default=False)

    # किती वेळा डाउनलोड केलंय ते ट्रॅक करेल
    retry_count = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'devopsvaultx_payments'
        verbose_name = "DevOpsVaultX Payment"
        verbose_name_plural = "DevOpsVaultX Payments"

    def __str__(self):
        user_info = self.email if self.email else "Guest"
        return f"{self.product.title} | {user_info} | {self.status}"