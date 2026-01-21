from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price')  # changed 'name' → 'title'
    search_fields = ('title', 'category')
