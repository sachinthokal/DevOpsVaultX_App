from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class ToolStaticSitemap(Sitemap):
    priority = 0.9 
    changefreq = 'weekly'

    def items(self):

        links = [ 
            'tools:tool_home',
            'tools:json_fix',
            'tools:yaml_json',
            'tools:beautify',
            'tools:base64',
            'tools:secret_gen',
            'tools:case_converter',
        ]
        return links

    def location(self, item):
        
        return reverse(item)