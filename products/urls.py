# products/urls.py
from django.urls import path
from products import views

app_name = "products"

urlpatterns = [
    path('', views.product_list, name='list'),
    path('<int:pk>/', views.product_detail, name='details'),

    # NEW 👇
    path('<int:pk>/buy/', views.buy_now, name='buy_now'),
    ]
