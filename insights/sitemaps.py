from django.contrib.sitemaps import Sitemap
from .models import InsightsPost

class InsightDynamicSitemap(Sitemap):
    priority = 0.9
    changefreq = 'daily'

    def items(self):
        active_posts = InsightsPost.objects.filter(is_published=True)
        return active_posts

    def lastmod(self, obj):
        return obj.created_at