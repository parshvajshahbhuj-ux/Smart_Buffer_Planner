#!/usr/bin/env python
"""
Smart Buffer Planner - Initial Setup Script
Run: python setup.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.management import call_command
from accounts.models import User

print("=" * 50)
print("  Smart Buffer Planner - Setup")
print("=" * 50)

print("\n[1/4] Running migrations...")
call_command('migrate', verbosity=0)
print("  ✓ Migrations complete")

print("\n[2/4] Seeding initial dish data...")
call_command('seed_data')
print("  ✓ Dishes and categories loaded")

print("\n[3/4] Creating admin user...")
if not User.objects.filter(email='admin@buffet.com').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@buffet.com',
        password='Admin@123',
        role='admin'
    )
    print("  ✓ Admin created: admin@buffet.com / Admin@123")
else:
    print("  ✓ Admin already exists")

print("\n[4/4] Creating demo user...")
if not User.objects.filter(email='demo@buffet.com').exists():
    User.objects.create_user(
        username='demo',
        email='demo@buffet.com',
        password='Demo@123',
        role='caterer',
        organization='Demo Catering Co.'
    )
    print("  ✓ Demo user created: demo@buffet.com / Demo@123")
else:
    print("  ✓ Demo user already exists")

print("\n" + "=" * 50)
print("  Setup complete!")
print("  Run: python manage.py runserver")
print("  Visit: http://127.0.0.1:8000")
print("=" * 50)
