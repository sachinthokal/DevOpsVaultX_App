from django.urls import path
from . import views

app_name = "vault"

urlpatterns = [
    path("", views.vault_home, name="home"),
    path("vault/<slug:slug>/", views.vault_detail, name="detail"),
]
