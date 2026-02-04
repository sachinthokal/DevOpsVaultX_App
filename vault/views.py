from django.shortcuts import render, get_object_or_404
from .models import VaultPost

def vault_home(request):
    posts = VaultPost.objects.filter(is_published=True)

    context = {
        "news": posts.filter(category="news"),
        "blogs": posts.filter(category="blog"),
        "offers": posts.filter(category="offer"),
    }
    return render(request, "vault/vault_home.html", context)


def vault_detail(request, slug):
    post = get_object_or_404(VaultPost, slug=slug, is_published=True)
    return render(request, "vault/vault_detail.html", {"post": post})
