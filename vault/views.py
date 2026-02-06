from django.http import HttpResponse
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


def vault_detail(request,category, slug):
    post = get_object_or_404(VaultPost,slug=slug,category=category,is_published=True)

    response = render(
        request,
        "vault/vault_detail.html",
        {"post": post}
    )
    return response

# def vault_detail(request, category, slug):
#     # Only raise error for testing
#     res = 1 / 0  # force exception
#     return HttpResponse(res)

