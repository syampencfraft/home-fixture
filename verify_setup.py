import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home.settings')
django.setup()

from django.conf import settings
from fixture.models import Category, Service, ServiceProfessional

print(f"BASE_DIR: {settings.BASE_DIR}")
print(f"Database: {settings.DATABASES['default']['NAME']}")

print("\n--- Categories ---")
for cat in Category.objects.all():
    print(f"[{cat.id}] {cat.name}")

print("\n--- Services ---")
for svc in Service.objects.all():
    print(f"[{svc.id}] {svc.name} - Category: {svc.category.name} (ID: {svc.category_id})")

print("\n--- Professionals ---")
for pro in ServiceProfessional.objects.all():
    cat_name = pro.category.name if pro.category else "NONE"
    cat_id = pro.category_id if pro.category else "NONE"
    print(f"[{pro.id}] {pro.user.username} - Category: {cat_name} (ID: {cat_id})")
