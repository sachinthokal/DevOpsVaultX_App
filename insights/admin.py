from django.contrib import admin
from .models import InsightsPost

@admin.register(InsightsPost)
class InsightsPostAdmin(admin.ModelAdmin):
    list_display = (
        "title", "category", "is_published",
        "is_pinned", "mark_new", "priority", "created_at"
    )
    list_editable = ("is_pinned", "mark_new", "priority")
    list_filter = ("category", "is_published")
    prepopulated_fields = {"slug": ("title",)}
