from django.db import models

class SystemLog(models.Model):
    message = models.CharField(max_length=255)
    log_type = models.CharField(max_length=50) 
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # डेटाबेसमध्ये टेबलचं नाव 'devopsvaultx_SystemLog' असेल
        db_table = 'devopsvaultx_systemlogs'
        
        # Django Admin मध्ये दिसणारी नावे
        verbose_name = "DevOpsVaultX System Log"
        verbose_name_plural = "DevOpsVaultX System Logs"
        
        # नवीन लॉग्स सर्वात वर दिसण्यासाठी
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.log_type}: {self.message[:50]}"