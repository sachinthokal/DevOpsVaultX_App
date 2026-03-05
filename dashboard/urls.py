from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('get-latest-logs/', views.get_latest_logs, name='get_logs')
]