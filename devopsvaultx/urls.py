"""
URL configuration for devopsvaultx project.
"""
from django.contrib import admin
from django.urls import include, path

# --- Required imports for handling media/image files ---
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls), # Replace at time live
    path('', include('pages.urls')),               # Home / About / Contact
    path('products/', include('products.urls')),  # Products
    path('payments/', include('payments.urls')),  # Payment app include 
]

# Media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)