from django.db import models
from products.models import Product

class Payment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.title} - {'Paid' if self.paid else 'Pending'}"
