from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [
    path('', views.tool_home, name='tool_home'),
    path('json-fix/', views.json_fix_view, name='json_fix'), # Matches {% url 'tools:json_fix' %}
]