from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        # Static pages
        links = ['pages:home', 'pages:about', 'pages:contact', 'products:list','vaultx:index','insights:home']
        # print(f"DEBUG: Static Sitemap found {len(links)} links")
        return links

    def location(self, item):
        return reverse(item)

class ProductSitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        # FIX: Products variable
        all_products = Product.objects.all()
        # print(f"DEBUG: Product Sitemap found {all_products.count()} products")
        return all_products

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse('products:details', kwargs={'pk': obj.pk})