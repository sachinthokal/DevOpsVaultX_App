from django.urls import path
from . import views

app_name = "insights"

urlpatterns = [
    path("", views.insights_home, name="home"),
    # 🔥 category + slug
    path("<str:category>/<slug:slug>", views.insights_home_detail, name="detail"),]
