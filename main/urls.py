from django.urls import path, re_path
from .views import pages

urlpatterns = [
    # Specific routes (if you want different entry points for different sections)
    path("", pages.home_view, name="home"),
    path("profile/", pages.profile_view, name="profile"),
    path("rooms/", pages.rooms_view, name="rooms"),
    
    # Option 1: Catch-all pattern for SPA frontend routing
    # This will let your frontend handle all routing
    # BUT exclude API routes and specific routes
    re_path(r'^(?!api/|profile/|rooms/).*/$', pages.catch_all_view, name="catch_all"),
]
