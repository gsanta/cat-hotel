import uuid
from django.db import models
from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser

# Create your models here.

class User(AbstractBaseUser):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    email = models.EmailField(unique=True)  # TEXT NOT NULL UNIQUE with email validation
    password = models.TextField()  # TEXT NOT NULL - store hashed passwords
    last_login = models.DateTimeField(blank=True, null=True)  # Required for Django auth
    created_at = models.DateTimeField(
        default=timezone.now
    )  # TIMESTAMPTZ NOT NULL DEFAULT NOW()
    updated_at = models.DateTimeField(
        auto_now=True
    )  # TIMESTAMPTZ with auto-update trigger equivalent
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email'], name='idx_users_email'),
        ]

class Room(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=255)  # VARCHAR(255) NOT NULL
    address = models.CharField(max_length=255)  # VARCHAR(255) NOT NULL
    created_at = models.DateTimeField(
        default=timezone.now
    )  # TIMESTAMPTZ NOT NULL DEFAULT NOW()
    updated_at = models.DateTimeField(
        auto_now=True
    )  # TIMESTAMPTZ with auto-update trigger equivalent
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'rooms'

class Cat(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=255)  # VARCHAR(255) NOT NULL
    owner_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cats'
    )  # REFERENCES users(id) ON DELETE CASCADE
    created_at = models.DateTimeField(
        default=timezone.now
    )  # TIMESTAMPTZ NOT NULL DEFAULT NOW()
    updated_at = models.DateTimeField(
        auto_now=True
    )  # TIMESTAMPTZ with auto-update trigger equivalent
    
    def __str__(self):
        return f"{self.name} ({self.owner_user.email})"
    
    class Meta:
        db_table = 'cats'
        indexes = [
            models.Index(fields=['owner_user'], name='idx_cats_owner_user_id'),
        ]


class BookingQuerySet(models.QuerySet):
    """Custom QuerySet for Booking model with reusable query methods"""
    
    def for_user(self, user):
        """Filter bookings by user"""
        return self.filter(user=user)
    
    def paginated(self, page=1, page_size=10):
        """
        Returns a dict with paginated items and total count.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
        
        Returns:
            dict with 'items' (QuerySet) and 'total_count' (int)
        """
        total_count = self.count()
        offset = (page - 1) * page_size
        items = self[offset:offset + page_size]
        return {
            'items': items,
            'total_count': total_count
        }


class BookingManager(models.Manager):
    """Custom Manager for Booking model"""
    
    def get_queryset(self):
        return BookingQuerySet(self.model, using=self._db)
    
    def for_user(self, user):
        return self.get_queryset().for_user(user)


class Booking(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )  # REFERENCES users(id) ON DELETE CASCADE
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE
    )  # REFERENCES rooms(id) ON DELETE CASCADE
    start_date = models.DateTimeField()  # TIMESTAMPTZ NOT NULL
    end_date = models.DateTimeField()  # TIMESTAMPTZ NOT NULL
    food_from_owner = models.BooleanField(
        default=False
    )  # BOOLEAN NOT NULL DEFAULT FALSE
    notes = models.TextField(
        blank=True,
        null=True
    )  # TEXT (optional)
    created_at = models.DateTimeField(
        default=timezone.now
    )  # TIMESTAMPTZ NOT NULL DEFAULT NOW()
    updated_at = models.DateTimeField(
        auto_now=True
    )  # TIMESTAMPTZ with auto-update trigger equivalent
    
    def __str__(self):
        return f"{self.user.email} - {self.room.name} ({self.start_date.date()})"
    
    objects = BookingManager()
    
    class Meta:
        db_table = 'bookings'

class BookingCat(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='booking_cats'
    )  # REFERENCES bookings(id) ON DELETE CASCADE
    cat = models.ForeignKey(
        Cat,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )  # REFERENCES cats(id) ON DELETE SET NULL
    guest_cat_name = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )  # VARCHAR(255) for non-registered cats
    created_at = models.DateTimeField(
        default=timezone.now
    )  # TIMESTAMPTZ NOT NULL DEFAULT NOW()
    
    def clean(self):
        """Ensure either cat_id OR guest_cat_name is provided, but not both"""
        if self.cat and self.guest_cat_name:
            raise ValidationError("Cannot specify both registered cat and guest cat name")
        if not self.cat and not self.guest_cat_name:
            raise ValidationError("Must specify either a registered cat or guest cat name")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        cat_name = self.cat.name if self.cat else self.guest_cat_name
        return f"{self.booking} - {cat_name}"
    
    class Meta:
        db_table = 'booking_cats'
        indexes = [
            models.Index(fields=['booking'], name='idx_booking_cats_booking_id'),
            models.Index(fields=['cat'], name='idx_booking_cats_cat_id'),
        ]
        constraints = [
            # Prevent duplicate registered cats in the same booking
            models.UniqueConstraint(
                fields=['booking', 'cat'],
                name='unique_booking_cat',
                condition=models.Q(cat__isnull=False)
            ),
            # Prevent duplicate guest cat names in the same booking
            models.UniqueConstraint(
                fields=['booking', 'guest_cat_name'],
                name='unique_booking_guest_cat',
                condition=models.Q(guest_cat_name__isnull=False)
            ),
            # Ensure either cat_id OR guest_cat_name is provided, but not both
            models.CheckConstraint(
                check=(
                    models.Q(cat__isnull=False, guest_cat_name__isnull=True) |
                    models.Q(cat__isnull=True, guest_cat_name__isnull=False)
                ),
                name='check_cat_reference'
            )
        ]

class Product(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.TextField()  # TEXT NOT NULL
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )  # NUMERIC(12,2) NOT NULL
    quantity = models.IntegerField()  # INTEGER NOT NULL
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'products'  # Keep the same table name as Go migration
