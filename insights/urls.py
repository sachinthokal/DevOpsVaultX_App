from django.urls import path
from . import views

app_name = "vault"

urlpatterns = [
    path("", views.vault_home, name="home"),
    # 🔥 category + slug
    path("<str:category>/<slug:slug>", views.vault_detail, name="detail"),
    # path("vault/<slug:slug>/", views.vault_detail, name="detail"),
]
