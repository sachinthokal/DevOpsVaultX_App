from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    # इथे name="buy_product" जोडणे आवश्यक आहे
    path("buy/<int:pk>/", views.buy_product, name="buy_product"), 
    
    path("success/<int:pk>/", views.payment_success, name="payment_success"),
    path("failed/", views.payment_failed, name="payment_failed"),
    path("retry/<str:order_id>/", views.retry_payment, name="retry_payment"),
    path("webhook/razorpay/", views.razorpay_webhook, name="razorpay_webhook"),
    path('vault/', views.user_vault, name='user_vault'),
]