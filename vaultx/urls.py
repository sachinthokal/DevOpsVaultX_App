# vaultx/urls.py
from django.urls import path
from . import views

app_name = 'vaultx'

urlpatterns = [
    path('', views.vaultx_home, name='index'),
    path('delete-item/<int:payment_id>/', views.delete_vault_item, name='delete_vault_item'),
]