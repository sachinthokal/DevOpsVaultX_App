# db_monitor/admin.py
from django.contrib import admin
from django.template.response import TemplateResponse
from .models import DBSize
from .utils.db_size import generate_db_size_report

@admin.register(DBSize)
class DBSizeAdmin(admin.ModelAdmin):
    change_list_template = "admin/db_size.html"

    def get_queryset(self, request):
        return super().get_queryset(request).none()  # avoid table queries

    def changelist_view(self, request, extra_context=None):
        report = generate_db_size_report()
        context = {"report": report}
        return TemplateResponse(request, "admin/db_size.html", context)
