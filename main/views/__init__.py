# Views package for the main app
# Import all views for backward compatibility

from .auth import register_user, login_view, logout_user, change_password
from .booking import create_booking, delete_booking
from .pages import (
    spa_view,
    spa_login_required,
    home_view,
    rooms_view,
    profile_view,
    catch_all_view,
)

__all__ = [
    # Auth views
    'register_user',
    'login_view',
    'logout_user',
    'change_password',
    # Booking views
    'create_booking',
    'delete_booking',
    # Page views
    'spa_view',
    'spa_login_required',
    'home_view',
    'rooms_view',
    'profile_view',
    'catch_all_view',
]
