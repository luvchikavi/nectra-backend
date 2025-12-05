#!/usr/bin/env python
"""
Create a superuser for Django admin
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.users.models import User

# Create superuser
username = 'admin'
email = 'admin@nectar.local'
password = 'admin123'

if User.objects.filter(username=username).exists():
    print(f"✓ Superuser '{username}' already exists")
else:
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name='Admin',
        last_name='User'
    )
    print(f"✓ Superuser created successfully!")
    print(f"  Username: {username}")
    print(f"  Password: {password}")
    print(f"  Email: {email}")
