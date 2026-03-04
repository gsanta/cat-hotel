from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import make_password
import json
import logging

from ..serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserLoginSerializer,
    ChangePasswordSerializer,
)

# Get logger for this module
logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
def register_user(request):
    """
    Register a new user with email and password.
    
    POST /api/auth/register/
    {
        "email": "user@example.com",
        "password": "SecurePassword123",
        "password_confirm": "SecurePassword123"
    }
    """
    logger.info(f"Register endpoint called - Request body: {request.body}")
    logger.info(f"Request content type: {request.content_type}")
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON'
        }, status=400)
    
    serializer = UserRegistrationSerializer(data=data)
    
    logger.info(f"Registration attempt for email: {data.get('email', 'unknown')}")
    logger.info(f"Serializer is_valid(): {serializer.is_valid()}")
    
    if not serializer.is_valid():
        logger.error(f"Serializer errors: {serializer.errors}")
    
    if serializer.is_valid():
        try:
            with transaction.atomic():
                user = serializer.save()
                
                # Return user data (without password)
                user_serializer = UserSerializer(user)
                
                return JsonResponse({
                    'success': True,
                    'message': 'User registered successfully',
                    'user': user_serializer.data
                }, status=201)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Registration failed',
                'error': str(e)
            }, status=500)
    else:
        return JsonResponse({
            'success': False,
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=400)


@require_http_methods(["POST"])
def login_view(request):
    """
    Login user with email and password.
    
    POST /api/auth/login/
    {
        "email": "user@example.com",
        "password": "SecurePassword123"
    }
    """
    logger.info(f"Login endpoint called - Request body: {request.body}")
    logger.info(f"Request content type: {request.content_type}")
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON'
        }, status=400)
    
    serializer = UserLoginSerializer(data=data)
    
    logger.info(f"Login attempt for email: {data.get('email', 'unknown')}")
    logger.info(f"Serializer is_valid(): {serializer.is_valid()}")
    
    if not serializer.is_valid():
        logger.error(f"Serializer errors: {serializer.errors}")
    
    if serializer.is_valid():
        try:
            # Get the authenticated user from validated data
            user = serializer.validated_data['user']
            
            # Actually log the user in (creates Django session)
            login(request, user)
            logger.info(f"User {user.email} successfully logged in via Django auth")
            
            # Return user data (without password)
            user_serializer = UserSerializer(user)
            
            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'user': user_serializer.data
            }, status=200)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Login failed',
                'error': str(e)
            }, status=500)
    else:
        return JsonResponse({
            'success': False,
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=400)


@require_http_methods(["POST"])
def logout_user(request):
    """
    Logout user and clear Django session.
    
    POST /api/auth/logout/
    """
    logger.info(f"Logout endpoint called for user: {request.user}")
    
    if request.user.is_authenticated:
        user_email = request.user.email
        logout(request)
        logger.info(f"User {user_email} successfully logged out")
        
        return JsonResponse({
            "success": True,
            "message": "Logged out successfully"
        }, status=200)
    else:
        logger.info("Logout called for unauthenticated user")
        return JsonResponse({
            "success": True,
            "message": "Already logged out"
        }, status=200)


@require_http_methods(["POST"])
def change_password(request):
    """
    Change password for authenticated user.
    
    POST /api/auth/change-password/
    {
        "current_password": "OldPassword123",
        "new_password": "NewSecurePassword456",
        "new_password_confirm": "NewSecurePassword456"
    }
    """
    logger.info(f"Change password endpoint called by user: {request.user}")
    
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
    
    serializer = ChangePasswordSerializer(data=data, context={'user': request.user})
    
    if serializer.is_valid():
        try:
            # Update password
            request.user.password = make_password(serializer.validated_data['new_password'])
            request.user.save()
            
            logger.info(f"Password changed successfully for user: {request.user.email}")
            
            return JsonResponse({
                'success': True,
                'message': 'Password changed successfully'
            }, status=200)
            
        except Exception as e:
            logger.error(f"Password change failed: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Password change failed',
                'error': str(e)
            }, status=500)
    else:
        logger.error(f"Serializer errors: {serializer.errors}")
        return JsonResponse({
            'success': False,
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=400)
