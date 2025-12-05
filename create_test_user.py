import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.users.models import User

# Create test user
email = 'admin@nectra.com'
password = 'admin123'

try:
    user = User.objects.get(username=email)
    print(f'User {email} already exists')
except User.DoesNotExist:
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name='Admin',
        last_name='User',
        role='OFFICE_MANAGER',
        is_staff=True,
        is_superuser=True
    )
    print(f'Created user: {email} / {password}')
    print(f'Role: {user.role}')
