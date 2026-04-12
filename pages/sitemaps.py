from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class PagesStaticSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        # Static pages
        links = ['pages:home', 'pages:about', 'pages:contact', 'products:list', 'insights:home']
        # print(f"DEBUG: Static Sitemap found {len(links)} links")
        return links

    def location(self, item):
        return reverse(item)