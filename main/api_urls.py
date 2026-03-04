from django.urls import path
from .views import auth, booking

urlpatterns = [
    path('auth/register/', auth.register_user, name='api_register'),
    path('auth/login/', auth.login_view, name='api_login'),
    path('auth/logout/', auth.logout_user, name='api_logout'),
    path('auth/change-password/', auth.change_password, name='api_change_password'),
    path('bookings/', booking.create_booking, name='api_create_booking'),
    path('bookings/<uuid:booking_id>/', booking.delete_booking, name='api_delete_booking'),
]
