from django.urls import path
from . import views

app_name = 'vaultx'

urlpatterns = [
    path('', views.vaultx_home, name='index'),
]