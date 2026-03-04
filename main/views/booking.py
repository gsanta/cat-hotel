from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
import json
import logging

from ..models import Booking
from ..serializers import CreateBookingSerializer, BookingSerializer

# Get logger for this module
logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
def create_booking(request):
    """
    Create a new booking.
    
    POST /api/bookings/
    {
        "start_date": "2026-03-01T10:00:00Z",
        "end_date": "2026-03-05T14:00:00Z",
        "room_id": "a1b2c3d4-e5f6-4789-9abc-def012345678",
        "food_from_owner": false,
        "notes": "Please give extra attention",
        "cats": ["Whiskers", "Mittens"]
    }
    """
    logger.info(f"Create booking endpoint called by user: {request.user}")
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Authentication required'
        }, status=401)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON'
        }, status=400)
    
    serializer = CreateBookingSerializer(data=data, context={'request': request})
    
    logger.info(f"Booking creation attempt by user: {request.user.email}")
    
    if serializer.is_valid():
        try:
            with transaction.atomic():
                booking = serializer.save()
                
                # Return the created booking using BookingSerializer
                booking_serializer = BookingSerializer(booking, context={'request': request})
                
                return JsonResponse({
                    'success': True,
                    'message': 'Booking created successfully',
                    'booking': booking_serializer.data
                }, status=201)
                
        except Exception as e:
            logger.error(f"Booking creation failed: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Booking creation failed',
                'error': str(e)
            }, status=500)
    else:
        logger.error(f"Serializer errors: {serializer.errors}")
        return JsonResponse({
            'success': False,
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=400)


@require_http_methods(["DELETE"])
def delete_booking(request, booking_id):
    """
    Delete a booking by ID.
    
    DELETE /api/bookings/<booking_id>/
    
    Only the owner of the booking can delete it.
    Booking can only be deleted if start_date > now + 48 hours.
    """
    logger.info(f"Delete booking endpoint called by user: {request.user}, booking_id: {booking_id}")
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Authentication required'
        }, status=401)
    
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Booking not found'
        }, status=404)
    
    # Check ownership
    if booking.user_id != request.user.id:
        return JsonResponse({
            'success': False,
            'message': 'You do not have permission to delete this booking'
        }, status=403)
    
    # Check if booking is cancelable (start_date > now + 48 hours)
    cancellation_deadline = timezone.now() + timedelta(hours=48)
    if booking.start_date <= cancellation_deadline:
        return JsonResponse({
            'success': False,
            'message': 'Booking cannot be cancelled within 48 hours of start date'
        }, status=400)
    
    try:
        booking.delete()
        logger.info(f"Booking {booking_id} deleted successfully by user: {request.user.email}")
        
        return JsonResponse({
            'success': True,
            'message': 'Booking deleted successfully'
        }, status=200)
        
    except Exception as e:
        logger.error(f"Booking deletion failed: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Booking deletion failed',
            'error': str(e)
        }, status=500)
