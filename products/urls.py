# products/urls.py
from django.urls import path
from products import views

app_name = "products"

urlpatterns = [
    path('', views.product_list, name='list'),
    path('<int:pk>/', views.product_detail, name='detail'),

    # NEW 👇
    path('<int:pk>/buy/', views.buy_now, name='buy_now'),
    path('<int:pk>/confirm/', views.confirm_payment, name='confirm_payment'),
    path('<int:pk>/download/', views.download_file, name='download_file'),
]
