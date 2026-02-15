from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta

class VaultPost(models.Model):
    CATEGORY_CHOICES = [
        ('news', 'News'),
        ('blog', 'Blog'),
        ('offer', 'Offer'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    content = models.TextField()

    is_published = models.BooleanField(default=True)

    # 🔥 EXTRA FEATURES
    is_pinned = models.BooleanField(default=False)
    mark_new = models.BooleanField(default=False)
    priority = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 1. डेटाबेस टेबलचे नाव बदलण्यासाठी (तुमच्या आवडीचे नाव द्या)
        db_table = 'devopsvaultx_vault_posts' # सध्या हे 'vault_vaultpost' आहे
        
        # 2. ऑर्डरिंग आणि नावे
        ordering = ['-is_pinned', 'priority', '-created_at']
        verbose_name = "DevOpsVaultX Vault Post"
        verbose_name_plural = "DevOpsVaultX Vault Posts"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            # ड्युप्लिकेट स्लग टाळण्यासाठी लॉजिक
            while VaultPost.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    @property
    def is_new(self):
        # २ दिवसांच्या आतली पोस्ट 'New' दाखवण्यासाठी
        return self.created_at >= timezone.now() - timedelta(days=2)

    def __str__(self):
        return self.title