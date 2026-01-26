# db_monitor/models.py
from django.db import models

class DBSize(models.Model):
    class Meta:
        managed = False
        verbose_name = "DB Size Report"
        verbose_name_plural = "DB Size Reports"
