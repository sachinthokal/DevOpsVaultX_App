from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path('buy/<int:pk>/', views.buy_product, name='buy_product'),
    path('success/<int:pk>/', views.payment_success, name='payment_success'),
]
