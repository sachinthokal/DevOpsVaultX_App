from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('notes', 'Notes'),
        ('courses', 'Courses'),
        ('templates', 'Templates'),
        ('tools', 'Tools'),
    ]

    title = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    is_new = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Image for product preview
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    # File to sell (any type)
    file = models.FileField(upload_to='product_files/', null=False, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 1. डेटाबेस टेबलचे नाव बदलण्यासाठी
        db_table = 'devopsvaultx_products'
        
        # 2. ऑर्डरिंग आणि नावे
        ordering = ['-created_at', '-id']
        verbose_name = "DevOpsVaultX Product"
        verbose_name_plural = "DevOpsVaultX Products"

    def __str__(self):
        return self.title