# URL configuration for devopsvaultx project.
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve # Navin import
from django.urls import re_path # Navin import

urlpatterns = [
    path('admin/', admin.site.urls),

    # App URLs
    path('', include('pages.urls')),
    path('products/', include('products.urls')),
    path('payments/', include('payments.urls')),
    path('insights/', include('insights.urls')),
    path('vaultx/', include('vaultx.urls')),

    # SEO REQUIRED FILES
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path("sitemap.xml", TemplateView.as_view(template_name="sitemap.xml", content_type="application/xml")),

    # 🔥 DUSRYA USERS SATHI FIX (Production and Debug both)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

# Local development sathi he pan rahu dya
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)