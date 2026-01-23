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
    description = models.TextField()
    is_new = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # 1. Image field for product preview
    # upload_to creates a folder 'product_images' inside your media directory
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    
    # 2. Tracking creation time (Helpful for sorting)
    created_at = models.DateTimeField(auto_now_add=True)

    # 3. Meta class to handle sorting automatically
    class Meta:
        # '-created_at' ensures new products appear at the top
        ordering = ['-created_at', '-id']

    def __str__(self):
        return self.title