# URL configuration for devopsvaultx project.
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

# --- SITEMAP IMPORTS ---
from django.contrib.sitemaps.views import sitemap
from insights.sitemaps import InsightDynamicSitemap
from pages.sitemaps import PagesStaticSitemap
from products.sitemaps import ProductSitemap
from tools.sitemaps import ToolStaticSitemap
from vaultx.sitemaps import VaultxStaticSitemap 

# Sitemap Dictionary
sitemaps = {
    'pages': PagesStaticSitemap,
    'insights': InsightDynamicSitemap,
    'products': ProductSitemap,  
    'vaultx': VaultxStaticSitemap,
    'tools': ToolStaticSitemap,
}

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('admin-dashboard/', admin.site.urls),
    path('owner-dashboard/', include('dashboard.urls')),

    # App URLs
    path('', include('pages.urls')),
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('payments/', include('payments.urls')),
    path('insights/', include('insights.urls')),
    path('vaultx/', include('vaultx.urls')),
    path('tools/', include('tools.urls')),

    # SEO REQUIRED FILES
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    
    # 🔥 DYNAMIC SITEMAP FIX
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),

    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

# Local development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)