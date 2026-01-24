from django.contrib import admin
from .models import Product
from django.utils.html import format_html # Image dakhvnyasathi garjeche aahe

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'display_image', # List madhe choti image dakhvel
        'title',
        'category',
        'price',
        'is_new',
        'is_active',
        'created_at'
    )

    list_filter = (
        'category',
        'is_new',
        'is_active',
        'created_at'
    )

    search_fields = (
        'title',
        'description'
    )

    list_editable = (
        'price',
        'is_new',
        'is_active'
    )

    ordering = ('-created_at',)

    # Edit page var image preview dakhvnyasathi
    readonly_fields = ('created_at', 'image_preview')

    def display_image(self, obj):
        """Main Admin List madhe image dakhvte"""
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return "No Image"
    display_image.short_description = 'Image'

    def image_preview(self, obj):
        """Product edit kartaana mothi image dakhvte"""
        if obj.image:
            return format_html('<img src="{}" width="200" style="border-radius: 10px;" />', obj.image.url)
        return "No Image Preview"
    image_preview.short_description = 'Current Image Preview'

    # Form madhe fields cha sequence tharvnyasathi (Optional)
    fields = ('title', 'category', 'description', 'price', 'image', 'image_preview','file', 'is_new', 'is_active', 'created_at')