from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
from .models import User, Room, Booking, BookingCat
import re


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm')
        
    def validate_email(self, value):
        """Validate email format and uniqueness"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_password(self, value):
        """Validate password strength"""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one number.")
        
        return value
    
    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        
        # Remove password_confirm as it's not needed for creation
        attrs.pop('password_confirm', None)
        return attrs
    
    def create(self, validated_data):
        """Create user with hashed password"""
        # Hash the password using bcrypt (same as your Go implementation)
        validated_data['password'] = make_password(validated_data['password'])
        return User.objects.create(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data (excluding password and timestamps)"""
    class Meta:
        model = User
        fields = ('id', 'email')
        read_only_fields = ('id', 'email')


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate login credentials"""
        from django.contrib.auth.hashers import check_password
        
        email = attrs.get('email')
        password = attrs.get('password')
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")
        
        # Verify password
        if not check_password(password, user.password):
            raise serializers.ValidationError("Invalid email or password.")
        
        # Add user to validated data for later use
        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing user password"""
    current_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    def validate_new_password(self, value):
        """Validate password strength"""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one number.")
        
        return value

    def validate(self, attrs):
        """Validate current password and that new passwords match"""
        from django.contrib.auth.hashers import check_password
        
        user = self.context.get('user')
        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        
        # Verify current password
        if not check_password(current_password, user.password):
            raise serializers.ValidationError({"current_password": "Current password is incorrect."})
        
        # Check new passwords match
        if new_password != new_password_confirm:
            raise serializers.ValidationError({"new_password_confirm": "New passwords do not match."})
        
        return attrs


class RoomSerializer(serializers.ModelSerializer):
    """Serializer for room data"""
    class Meta:
        model = Room
        fields = ('id', 'name', 'address')
        read_only_fields = ('id', 'name', 'address')


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for booking data with computed fields"""
    is_current_user = serializers.SerializerMethodField()
    cancelable = serializers.SerializerMethodField()
    room_id = serializers.UUIDField(source='room.id', read_only=True)
    user_id = serializers.UUIDField(source='user.id', read_only=True)
    
    class Meta:
        model = Booking
        fields = ('id', 'start_date', 'end_date', 'room_id', 'user_id', 'is_current_user', 'cancelable')
        read_only_fields = ('id', 'start_date', 'end_date', 'room_id', 'user_id')
    
    def get_is_current_user(self, obj):
        """Check if the booking belongs to the currently logged in user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user_id == request.user.id
        return False
    
    def get_cancelable(self, obj):
        """Check if booking can be canceled (start_date > now + 48 hours)"""
        cancellation_deadline = timezone.now() + timedelta(hours=48)
        return obj.start_date > cancellation_deadline


class CreateBookingSerializer(serializers.Serializer):
    """Serializer for creating a new booking"""
    start_date = serializers.DateTimeField(required=True)
    end_date = serializers.DateTimeField(required=True)
    room_id = serializers.UUIDField(required=True)
    food_from_owner = serializers.BooleanField(default=False)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    cats = serializers.ListField(
        child=serializers.CharField(max_length=255),
        required=True,
        allow_empty=True
    )
    
    def validate_cats(self, value):
        """Validate that at least one cat name is provided"""
        if not value or len(value) == 0:
            raise serializers.ValidationError({
                "message": "At least one cat name is required.",
                "code": "ERR_TOO_FEW_CATS_PROVIDED",
                "value": 1
            })
        return value
    
    def validate_room_id(self, value):
        """Validate that the room exists"""
        if not Room.objects.filter(id=value).exists():
            raise serializers.ValidationError("Room not found.")
        return value
    
    def validate(self, attrs):
        """Validate booking dates"""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError("End date must be after start date.")
        
        return attrs
    
    def create(self, validated_data):
        """Create booking and associated booking cats"""
        cats = validated_data.pop('cats', [])
        room_id = validated_data.pop('room_id')
        user = self.context['request'].user
        
        # Create the booking
        booking = Booking.objects.create(
            user=user,
            room_id=room_id,
            start_date=validated_data['start_date'],
            end_date=validated_data['end_date'],
            food_from_owner=validated_data.get('food_from_owner', False),
            notes=validated_data.get('notes')
        )
        
        # Create booking cats with guest_cat_name
        for cat_name in cats:
            BookingCat.objects.create(
                booking=booking,
                guest_cat_name=cat_name
            )
        
        return booking
