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

    razorpay_order_id = models.CharField(
        max_length=100,
        unique=True,
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

    retry_count = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.title} | {self.razorpay_order_id} | {self.status}"
