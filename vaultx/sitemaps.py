from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class VaultxStaticSitemap(Sitemap):
    priority = 0.9 
    changefreq = 'weekly'

    def items(self):

        links = [ 
            'vaultx:index',
        ]
        return links

    def location(self, item):
        
        return reverse(item)