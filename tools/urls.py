from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [
    path('', views.tool_home, name='tool_home'),
    path('json-fix/', views.json_fix_view, name='json_fix'), # Matches {% url 'tools:json_fix' %}
    path('yaml-json/', views.yaml_json_view, name='yaml_json'), # Matches {% url 'tools:yaml_json' %}
    path('beautify/', views.beautify_view, name='beautify'), # Matches {% url 'tools:beautify' %}
    path('base64/', views.base64_view, name='base64'), # Matches {% url 'tools:base64' %}
    path('secret-gen/', views.secret_gen_view, name='secret_gen'), # Matches {% url 'tools:secret_gen' %}
    path('case-converter/', views.case_converter_view, name='case_converter'), # Matches {% url 'tools:case_converter' %}
]