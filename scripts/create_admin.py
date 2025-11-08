import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "erms_project.settings")

import django

django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com")
PASSWORD = os.environ.get("ADMIN_PASSWORD")

user, created = User.objects.get_or_create(
    username=USERNAME,
    defaults={"email": EMAIL}
)
if created:
    password_to_set = PASSWORD or User.objects.make_random_password()
    user.set_password(password_to_set)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    if PASSWORD:
        print("Admin user created with provided password.")
    else:
        print(f"Admin user created with generated password: {password_to_set}")
else:
    if user.is_superuser:
        print("Admin user already exists.")
    else:
        user.email = EMAIL
        user.is_staff = True
        user.is_superuser = True
        password_to_set = PASSWORD or User.objects.make_random_password()
        user.set_password(password_to_set)
        user.save()
        if PASSWORD:
            print("Existing user promoted to superuser with provided password.")
        else:
            print(f"Existing user promoted to superuser with generated password: {password_to_set}")
