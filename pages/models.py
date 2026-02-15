from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # १. डेटाबेस टेबलचे नाव बदलण्यासाठी
        db_table = 'devopsvaultx_contact_messages'
        
        # २. ॲडमिन पॅनेलमध्ये सुटसुटीत नाव दिसण्यासाठी
        verbose_name = "DevOpsVaultX Contact Message"
        verbose_name_plural = "DevOpsVaultX Contact Messages"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.email}"