import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Product


@receiver(post_delete, sender=Product)
def delete_files_on_product_delete(sender, instance, **kwargs):
    """
    Product delete झाला → image + file media मधून delete
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(pre_save, sender=Product)
def delete_old_files_on_update(sender, instance, **kwargs):
    """
    Product update झाला आणि new image/file आला →
    old file safely delete
    """
    if not instance.pk:
        return  # New object

    try:
        old_product = Product.objects.get(pk=instance.pk)
    except Product.DoesNotExist:
        return

    # Image change
    if old_product.image and old_product.image != instance.image:
        if os.path.isfile(old_product.image.path):
            os.remove(old_product.image.path)

    # File change
    if old_product.file and old_product.file != instance.file:
        if os.path.isfile(old_product.file.path):
            os.remove(old_product.file.path)
