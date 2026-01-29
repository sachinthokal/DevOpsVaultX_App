# URL configuration for devopsvaultx project.
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

# --- Required imports for handling media/image files ---
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Replace at time live

    # App URLs
    path('', include('pages.urls')),               # Home / About / Contact
    path('products/', include('products.urls')),  # Products
    path('payments/', include('payments.urls')),  # Payments

    # 🔥 SEO REQUIRED FILES
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="robots.txt",
            content_type="text/plain"
        ),
    ),
    path(
        "sitemap.xml",
        TemplateView.as_view(
            template_name="sitemap.xml",
            content_type="application/xml"
        ),
    ),
]

# Media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
