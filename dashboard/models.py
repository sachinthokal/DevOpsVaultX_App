from django.db import models

class SystemLog(models.Model):
    message = models.CharField(max_length=255)
    log_type = models.CharField(max_length=50) 
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Table name in the database
        db_table = 'devopsvaultx_systemlogs'
        
        # Display names in Django Admin
        verbose_name = "DevOpsVaultX System Log"
        verbose_name_plural = "DevOpsVaultX System Logs"
        
        # Default ordering: Newest logs first for queries
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.log_type}: {self.message[:50]}"

    def save(self, *args, **kwargs):
        """
        Custom save method to handle automatic log cleanup.
        Maintains a healthy DB size by deleting old records in batches.
        """
        # 1. Save the current log entry first
        super().save(*args, **kwargs)
        
        # 2. Cleanup Configuration
        # Threshold is 150 (100 + 50)
        MAX_LOGS = 500
        BUFFER = 50
        
        # 3. Get total count
        current_count = SystemLog.objects.count()
        
        # 4. If count exceeds 150, trigger batch delete
        if current_count > (MAX_LOGS + BUFFER):
            # IMPORTANT: Get IDs of the oldest records.
            # Using list() forces the query to execute immediately.
            # Explicitly ordering by 'id' (Ascending) to get the oldest entries.
            old_log_ids = list(
                SystemLog.objects.all()
                .order_by('id')[:BUFFER]
                .values_list('id', flat=True)
            )
            
            # 5. Perform bulk delete
            if old_log_ids:
                SystemLog.objects.filter(id__in=old_log_ids).delete()