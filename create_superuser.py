import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dnd_app.settings')
django.setup()

from campaigns.models import User

# Check if superuser exists
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
        real_name='Administrator'
    )
    print("[OK] Superuser 'admin' created successfully!")
    print("  Username: admin")
    print("  Password: admin123")
    print("\n[!] Remember to change the password after first login!")
else:
    print("Superuser 'admin' already exists.")