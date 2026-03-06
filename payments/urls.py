from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [

    # 0. Blank payment page for test case
    path("", views.some_index_view, name="index"),

    # १. Product खरेदी करण्यासाठी आणि पेमेंट पेज दाखवण्यासाठी
    path("buy/<int:pk>/", views.buy_product, name="buy_product"), 
    
    # २. OTP प्रणालीसाठी नवीन पाथ (हे अ‍ॅड केले आहेत)
    path("send-otp/", views.send_otp, name="send_otp"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),

    # ३. पेमेंट स्टेटस आणि रिझल्टसाठी
    path("success/<int:pk>/", views.payment_success, name="payment_success"),
    path('<int:pk>/payment-result/', views.payment_result, name='payment_result'),
]