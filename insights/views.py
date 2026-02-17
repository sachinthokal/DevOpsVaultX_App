
from django.shortcuts import render, get_object_or_404
from .models import InsightsPost

def insights_home(request):
    posts = InsightsPost.objects.filter(is_published=True)

    context = {
        "news": posts.filter(category="news"),
        "blogs": posts.filter(category="blog"),
        "offers": posts.filter(category="offer"),
    }
    return render(request, "insights/insights_home.html", context)


def insights_home_detail(request,category, slug):
    post = get_object_or_404(InsightsPost,slug=slug,category=category,is_published=True)

    response = render(
        request,
        "insights/insights_detail.html",
        {"post": post}
    )
    return response

# def insights_detail(request, category, slug):
#     # Only raise error for testing
#     res = 1 / 0  # force exception
#     return HttpResponse(res)

