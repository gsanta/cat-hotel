import uuid
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from main.models import User, Product, Room, Booking


class Command(BaseCommand):
    help = 'Seeds the database with development data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Booking.objects.all().delete()
            Product.objects.all().delete()
            Room.objects.all().delete()
            User.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Cleared existing data'))

        self.stdout.write('Seeding database with development data...')
        
        # Create users
        self.create_users()
        
        # Create products
        self.create_products()
        
        # Create rooms
        self.create_rooms()
        
        # Create bookings
        self.create_bookings()
        
        self.stdout.write(self.style.SUCCESS('✓ Database seeded successfully!'))

    def create_users(self):
        from django.contrib.auth.hashers import make_password
        
        users_data = [
            {
                'id': 'eacc781f-6480-462a-adf7-a6e276aee761',
                'email': 'john.doe@example.com',
                'password': 'Testpassword1'  # Will be hashed below
            },
            {
                'id': '149e1f14-9db9-4eaa-b076-ad0a70907215',
                'email': 'jane.smith@example.com',
                'password': 'Testpassword1'  # Will be hashed below
            }
        ]
        
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                id=user_data['id'],
                defaults={
                    'email': user_data['email'],
                    'password': make_password(user_data['password'])  # Proper Django hashing
                }
            )
            if created:
                self.stdout.write(f'Created user: {user.email}')
            else:
                self.stdout.write(f'User already exists: {user.email}')

    def create_products(self):
        products_data = [
            ('75014105-27ee-4eaf-8060-3315af8b64c2', 'Cat Food Salmon', 12.99, 20),
            ('06685d32-8477-43c4-9dc4-aed302b06101', 'Cat Food Chicken', 11.49, 15),
            ('c8ae60e3-c9d7-4687-8af6-f8875ab62640', 'Cat Food Tuna', 13.25, 18),
            ('743f78df-ec6c-4c42-951a-3d12792db380', 'Catnip Toy Mouse', 4.99, 30),
            ('b105b5ec-ec27-41b3-b75d-7ed00dddb8ba', 'Catnip Toy Ball', 3.49, 25),
            ('a62d93c7-b5a6-4781-a10b-e6bc948de04b', 'Feather Wand', 7.99, 12),
            ('71911e5e-cf2a-45fa-852b-b18ea4689771', 'Laser Pointer', 8.50, 10),
            ('dc4982ef-c51a-4d4d-a436-4563a5d6e055', 'Scratching Post', 29.99, 5),
            ('c1cfdc7d-0c55-4497-b4f8-e284c53ee9fc', 'Cat Bed Plush', 24.99, 7),
            ('d3b1e795-8d02-4779-abe0-ccc8b318fb57', 'Cat Tunnel', 15.99, 8),
            ('f7e89037-aa7e-40e8-99d1-2cfeaa09d169', 'Cat Litter 10kg', 16.99, 14),
            ('bd6fea80-a786-4645-aec2-06423ee291dd', 'Cat Litter 5kg', 9.99, 20),
            ('20955740-14c1-4984-805b-5723ea810847', 'Cat Treats Salmon', 5.99, 22),
            ('1ba44944-b969-4f25-9e2a-1543b0b767eb', 'Cat Treats Chicken', 5.49, 19),
            ('5bf51332-2299-49e8-b4e8-c2d9716985ff', 'Cat Collar Bell', 6.99, 13),
            ('1feaafed-114d-44c4-ba6a-9e8a9013a398', 'Cat Carrier', 34.99, 4),
            ('fcef5983-4591-4aec-95a2-8c2b4ec9c407', 'Cat Brush', 8.99, 11),
            ('e7937d53-fc02-4188-9c99-b638f47f1270', 'Cat Shampoo', 10.99, 9),
            ('ed51bd5c-4f56-4ccf-b0a4-48cd61298611', 'Cat Water Fountain', 39.99, 3),
            ('4e5d4406-b8dd-467f-8c01-0271c11aa0ab', 'Cat Tree Deluxe', 79.99, 2),
            ('995ce263-2770-407d-856e-36286083d939', 'Cat Harness', 14.99, 6),
            ('657f1750-fc2c-48e2-81b7-d539e8a6ec61', 'Cat Door', 22.99, 5)
        ]
        
        for product_id, name, price, quantity in products_data:
            product, created = Product.objects.get_or_create(
                id=product_id,
                defaults={
                    'name': name,
                    'price': Decimal(str(price)),
                    'quantity': quantity
                }
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')

    def create_rooms(self):
        rooms_data = [
            {
                'id': 'a1b2c3d4-e5f6-4789-9abc-def012345678',
                'name': 'Cozy Cat Suite',
                'address': '123 Whisker Lane, Cat City, CC 12345'
            },
            {
                'id': 'b2c3d4e5-f6a7-4890-9bcd-ef0123456789',
                'name': 'Luxury Feline Resort',
                'address': '456 Purr Avenue, Meowtown, MT 67890'
            }
        ]
        
        for room_data in rooms_data:
            room, created = Room.objects.get_or_create(
                id=room_data['id'],
                defaults={
                    'name': room_data['name'],
                    'address': room_data['address']
                }
            )
            if created:
                self.stdout.write(f'Created room: {room.name}')

    def create_bookings(self):
        # Get users and rooms
        john = User.objects.get(id='eacc781f-6480-462a-adf7-a6e276aee761')
        jane = User.objects.get(id='149e1f14-9db9-4eaa-b076-ad0a70907215')
        cozy_suite = Room.objects.get(id='a1b2c3d4-e5f6-4789-9abc-def012345678')
        luxury_resort = Room.objects.get(id='b2c3d4e5-f6a7-4890-9bcd-ef0123456789')
        
        now = timezone.now()
        
        bookings_data = [
            # Bookings for Cozy Cat Suite
            {
                'id': 'ed099142-54a9-4648-a94e-7820fee2bafb',
                'user': john,
                'room': cozy_suite,
                'start_date': now - timedelta(days=45),
                'end_date': now - timedelta(days=40)
            },
            {
                'id': '6705c2d2-9d61-4880-acbf-b20c3e8c7bf4',
                'user': jane,
                'room': cozy_suite,
                'start_date': now - timedelta(days=5),
                'end_date': now + timedelta(days=2)
            },
            {
                'id': 'def5dfaf-3a2a-4877-8008-838c56d7a0d8',
                'user': john,
                'room': cozy_suite,
                'start_date': now + timedelta(days=5),
                'end_date': now + timedelta(days=8)
            },
            {
                'id': 'dda008cb-e1f5-4b61-864e-bad0e7753e1a',
                'user': jane,
                'room': cozy_suite,
                'start_date': now + timedelta(days=15),
                'end_date': now + timedelta(days=20)
            },
            {
                'id': 'a8d3b714-cee4-4b09-bfc1-5ca6a80668d3',
                'user': john,
                'room': cozy_suite,
                'start_date': now + timedelta(days=22),
                'end_date': now + timedelta(days=28)
            },
            # Bookings for Luxury Feline Resort
            {
                'id': '6df2a429-2284-4b4a-8239-bbfc5a1d62b0',
                'user': jane,
                'room': luxury_resort,
                'start_date': now - timedelta(days=71),
                'end_date': now - timedelta(days=66)
            },
            {
                'id': 'cf93ab35-be35-4dd0-bdca-867f97a56216',
                'user': john,
                'room': luxury_resort,
                'start_date': now - timedelta(days=2),
                'end_date': now + timedelta(days=3)
            },
            {
                'id': '6ecc808a-2e31-4762-9c6c-aecc25091d88',
                'user': jane,
                'room': luxury_resort,
                'start_date': now + timedelta(days=20),
                'end_date': now + timedelta(days=28)
            }
        ]
        
        for booking_data in bookings_data:
            booking, created = Booking.objects.get_or_create(
                id=booking_data['id'],
                defaults={
                    'user': booking_data['user'],
                    'room': booking_data['room'],
                    'start_date': booking_data['start_date'],
                    'end_date': booking_data['end_date'],
                    'food_from_owner': False,
                    'notes': None
                }
            )
            if created:
                self.stdout.write(f'Created booking: {booking.user.email} -> {booking.room.name}')
