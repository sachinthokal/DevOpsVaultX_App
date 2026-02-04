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
        ordering = ['-is_pinned', 'priority', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while VaultPost.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    @property
    def is_new(self):
        return self.created_at >= timezone.now() - timedelta(days=2)

    def __str__(self):
        return self.title
