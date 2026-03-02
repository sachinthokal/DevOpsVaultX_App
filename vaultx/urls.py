# vaultx/urls.py
from django.urls import path
from . import views

app_name = 'vaultx'

urlpatterns = [
    path('', views.vaultx_home, name='index'),
    path('delete-item/<int:payment_id>/', views.delete_vault_item, name='delete_vault_item'),
    path('receipt/<str:order_id>/', views.generate_receipt_pdf, name='receipt_download'),
    path('download/<int:product_id>/<int:payment_id>/', views.download_file, name='download_file'),
    ]