from django.contrib.sitemaps import Sitemap
from .models import Product

class ProductSitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.created_at