# db_monitor/models.py
from django.db import models

class DBSize(models.Model):
    class Meta:
        managed = False
        # जॅंगोच्या अंतर्गत वापरासाठी टेबलचे नाव सुसंगत ठेवूया
        db_table = 'devopsvaultx_db_size_report'
        verbose_name = "DB Size Report"
        verbose_name_plural = "DB Size Reports"

# Navin Summary Tab sathi Proxy Model
class PaymentSummary(models.Model):
    class Meta:
        managed = False  # Database madhe table banvuychi garaj nahi
        # प्रॉक्सी मॉडेलसाठी सुद्धा एक सुसंगत नाव
        db_table = 'devopsvaultx_product_summary'
        verbose_name = "DevOpsVaultX Product Summary Report"
        verbose_name_plural = "DevOpsVaultX Product Summary Reports"