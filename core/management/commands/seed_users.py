from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from core.models import UserDetails

User = get_user_model()

class Command(BaseCommand):
    help = 'Create initial users for the application'

    def handle(self, *args, **kwargs):
        users_data = [
            {
                'id': 1,
                'username': 'superadmin',
                'first_name': 'Super',
                'last_name': 'Admin',
                'email': 'superadmin@gmail.com',
                'password': 'Abcd@123',
                'is_staff': True,
                'is_active': True,
                'is_superuser': True,
                'phone_number': '0987654321',
                'role': 'superadmin',
                'last_login': None,
                'date_joined': timezone.now()
            },
            {
                'id': 2,
                'username': 'groupadmin',
                'first_name': 'Group',
                'last_name': 'Admin',
                'email': 'groupadmin@gmail.com',
                'password': 'Abcd@123',
                'is_staff': True,
                'is_active': True,
                'is_superuser': False,
                'phone_number': '0987654322',
                'role': 'groupadmin', 
                'last_login': None,
                'date_joined': timezone.now()
            },
            {
                'id': 3,
                'username': 'user1',
                'first_name': 'User',
                'last_name': 'One',
                'email': 'user1@gmail.com',
                'password': 'Abcd@123',
                'is_staff': False,
                'is_active': True,
                'is_superuser': False,
                'phone_number': '0987654323',
                'role': 'user',
                'last_login': None,
                'date_joined': timezone.now()
            },
            {
                'id': 4,
                'username': 'user2',
                'first_name': 'User',
                'last_name': 'Two',
                'email': 'user2@gmail.com',
                'password': 'Abcd@123',
                'is_staff': False,
                'is_active': True,
                'is_superuser': False,
                'phone_number': '0987654324',
                'role': 'user',
                'last_login': None,
                'date_joined': timezone.now()
            }
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                id=user_data['id'],
                defaults={
                    'username': user_data['username'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'email': user_data['email'],
                    'is_staff': user_data['is_staff'],
                    'is_active': user_data['is_active'],
                    'is_superuser': user_data['is_superuser'],
                    'last_login': user_data['last_login'],
                    'date_joined': user_data['date_joined']
                }
            )

            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully created user: {user_data["username"]}'))

                UserDetails.objects.create(
                    user=user,
                    phone_number=user_data['phone_number'],
                    role=user_data['role']
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created user details for: {user_data["username"]}'))
            else:
                self.stdout.write(self.style.WARNING(f'User {user_data["username"]} already exists.'))

            if user_data['is_superuser']:
                group, _ = Group.objects.get_or_create(name='superadmin')
                user.groups.add(group)
            elif user_data['is_staff']:
                group, _ = Group.objects.get_or_create(name='groupadmin')
                user.groups.add(group)

            user.save()
