
from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('notes','Notes'),
        ('courses','Courses'),
        ('templates','Templates'),
        ('tools','Tools'),
    ]
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.IntegerField()
    description = models.TextField()
    def __str__(self):
        return self.title