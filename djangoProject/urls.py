# djangoProject/urls.py
from django.contrib import admin
from django.urls import path, include
from .views import home
from . import views


urlpatterns = [
    path('list-urls/', views.list_urls, name='list_urls'),

    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('users/', include('users.urls', namespace='users')),  # Include the users app with namespace
    path('events/', include(('events.urls', 'events'), namespace='events')),
    path('registration/', include(('registration.urls', 'registration'), namespace='registration')),

    path('management/', include('management.urls')),
    path('checkin/', include('checkin.urls')),
    path('badges/', include('badges.urls')),
    # other URL patterns
]