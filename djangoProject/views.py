# djangoProject/views.py
from django.shortcuts import render
from django.urls import get_resolver
from django.http import JsonResponse

def list_urls(request):
    resolver = get_resolver()
    all_urls = []

    for url_pattern in resolver.url_patterns:
        try:
            # Try to get the pattern's name or path
            pattern_str = url_pattern.pattern.describe()  # This gives a description of the URL pattern
            all_urls.append(pattern_str)
        except AttributeError:
            # Skip patterns that don't have a `pattern.describe()` method
            continue

    # Filter admin URLs
    admin_urls = [url for url in all_urls if 'admin' in url]

    return JsonResponse({"admin_urls": admin_urls, "all_urls": all_urls})

def home(request):
    return render(request, 'home.html')