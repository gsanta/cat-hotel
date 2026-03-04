from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import redirect
import json
import logging

from ..manifest_client import get_js_files, get_css_files
from ..serializers import UserSerializer, RoomSerializer, BookingSerializer
from ..models import Room, Booking

# Get logger for this module
logger = logging.getLogger(__name__)


def spa_view(request, entry_point="pages/home/entry", page_props=None):
    """
    Generic single-page application view that can serve different frontend entry points.
    The frontend will handle routing and page rendering.
    
    Args:
        request: Django request object
        entry_point: Manifest entry point for assets
        page_props: Dictionary of props to inject into window.pageProps
    """
    if page_props is None:
        page_props = {}
    
    js_files = get_js_files(entry_point)
    css_files = get_css_files(entry_point)
    
    # Get CSRF token for this request
    csrf_token = get_token(request)
    
    # Serialize page props to JSON for injection
    page_props_json = json.dumps(page_props, indent=2)
    
    context = {
        'js_files': js_files,
        'css_files': css_files,
        'entry_point': entry_point,
        'page_props': page_props,
    }
    
    # Generic HTML shell for SPA
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="csrf-token" content="{csrf_token}">
        <title>Cat Hotel</title>
        {''.join(f'<link rel="stylesheet" href="{css}">' for css in css_files)}
    </head>
    <body>
        <div id="react-mount"></div>
        
        <!-- Inject page props for frontend consumption -->
        <script>
            window.pageProps = {page_props_json};
        </script>
        
        {''.join(f'<script src="{js}"></script>' for js in js_files)}
    </body>
    </html>
    """
    
    return HttpResponse(html)


def spa_login_required(redirect_to='home'):
    """Custom login required decorator for SPA views"""
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                logger.warning(f"Unauthenticated access to {view_func.__name__}")
                return redirect(redirect_to)
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def home_view(request):
    # Check if user is authenticated and serialize user data
    logger.info(f"Home view - request.user.is_authenticated: {request.user.is_authenticated}")
    logger.info(f"Home view - request.user: {request.user}")
    
    user_data = None
    if request.user.is_authenticated:
        user_serializer = UserSerializer(request.user)
        user_data = user_serializer.data
        logger.info(f"Home view - user_data: {user_data}")
    
    page_props = {
        "user": user_data
    }
    return spa_view(request, "pages/home/entry", page_props)


@spa_login_required()
def rooms_view(request):

    user_data = None
    if request.user.is_authenticated:
        user_serializer = UserSerializer(request.user)
        user_data = user_serializer.data
        logger.info(f"Rooms view - user_data: {user_data}")
    
    # Query all rooms from database
    rooms = Room.objects.all()
    room_serializer = RoomSerializer(rooms, many=True)
    
    # Query all bookings from database
    bookings = Booking.objects.all()
    booking_serializer = BookingSerializer(bookings, many=True, context={'request': request})
    
    page_props = {
        "user": user_data,
        "rooms": room_serializer.data,
        "bookings": booking_serializer.data
    }
    return spa_view(request, "pages/rooms/entry", page_props)


@spa_login_required()
def profile_view(request):

    user_data = None
    if request.user.is_authenticated:
        user_serializer = UserSerializer(request.user)
        user_data = user_serializer.data
        logger.info(f"Profile view - user_data: {user_data}")
    
    # Query all rooms from database
    rooms = Room.objects.all()
    room_serializer = RoomSerializer(rooms, many=True)
    
    # Query bookings for the current user only with pagination
    paginated_bookings = Booking.objects.for_user(request.user).paginated(page=1, page_size=10)
    booking_serializer = BookingSerializer(paginated_bookings['items'], many=True, context={'request': request})
    
    page_props = {
        "user": user_data,
        "rooms": room_serializer.data,
        "bookings": {
            "items": booking_serializer.data,
            "total_count": paginated_bookings['total_count']
        }
    }
    return spa_view(request, "pages/profile/entry", page_props)


def catch_all_view(request, path=""):
    """
    Catch-all view that serves the same SPA entry point for all routes.
    Let the frontend handle routing.
    """
    logger.info(f"Catch-all view - request.user.is_authenticated: {request.user.is_authenticated}")
    logger.info(f"Catch-all view - request.user: {request.user}")
    logger.info(f"Catch-all view - path: {path}")
    
    # Check if user is authenticated and serialize user data
    user_data = None
    if request.user.is_authenticated:
        user_serializer = UserSerializer(request.user)
        user_data = user_serializer.data
        logger.info(f"Catch-all view - user_data: {user_data}")
    
    page_props = {
        "page": "spa",
        "path": request.path,
        "user": user_data
    }
    return spa_view(request, "pages/home/entry", page_props)
