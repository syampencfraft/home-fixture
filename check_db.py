import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home.settings')
django.setup()

from fixture.models import Category, Service, ServiceProfessional

print("Categories:")
for cat in Category.objects.all():
    print(f"- {cat.id}: {cat.name}")

print("\nServices:")
for svc in Service.objects.all():
    print(f"- {svc.id}: {svc.name} (Category: {svc.category.name})")

print("\nProfessionals:")
for pro in ServiceProfessional.objects.all():
    print(f"- {pro.id}: {pro.user.username} (Category: {pro.category.name if pro.category else 'None'})")
