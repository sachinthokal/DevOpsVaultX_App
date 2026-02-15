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

    # 🔥 NEW FIELDS: Guest User चा डेटा साठवण्यासाठी
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(db_index=True, blank=True, null=True)

    # unique=True काढले आहे कारण FREE_ID मल्टिपल वेळा येऊ शकतो
    razorpay_order_id = models.CharField(
        max_length=100,
        db_index=True
    )

    # नवीन फिल्ड: Unique users ट्रॅक करण्यासाठी
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
        # १. डेटाबेस टेबलचे नाव बदलण्यासाठी
        db_table = 'devopsvaultx_payments'
        
        # २. ॲडमिन पॅनेलमध्ये सुटसुटीत नाव दिसण्यासाठी
        verbose_name = "DevOpsVaultX Payment"
        verbose_name_plural = "DevOpsVaultX Payments"

    def __str__(self):
        # Email असेल तर तो सुद्धा स्ट्रिंगमध्ये दिसेल, ओळखायला सोपे जाईल
        user_info = self.email if self.email else "Guest"
        return f"{self.product.title} | {user_info} | {self.status}"