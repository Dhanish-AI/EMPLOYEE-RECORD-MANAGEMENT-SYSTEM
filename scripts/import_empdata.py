import os
import sys
from decimal import Decimal
from pathlib import Path

from pymongo import MongoClient

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "erms_project.settings")

import django

django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction

from employees.models import Employee

CONNECTION_STRING = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("MONGODB_DB")
COLLECTION_NAME = os.environ.get("MONGODB_COLLECTION")
DEFAULT_PASSWORD = "Employee123!"

User = get_user_model()


def normalize_salary(value):
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def normalize_score(value):
    if value is None:
        return 0
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return 0


def as_str(value):
    if value is None:
        return ""
    return str(value)


def get_username(base: str):
    base = base.lower().replace(" ", "_")
    username = base
    suffix = 1
    while User.objects.filter(username=username).exists():
        suffix += 1
        username = f"{base}{suffix}"
    return username


def import_employees():
    if not CONNECTION_STRING:
        raise RuntimeError("MONGODB_URI environment variable is required for import_empdata.py")

    client = MongoClient(CONNECTION_STRING)
    collection = client[DB_NAME][COLLECTION_NAME]

    created = 0
    updated = 0

    with transaction.atomic():
        for document in collection.find():
            employee_id = document.get("employee_id")
            if not employee_id:
                continue

            email = document.get("email") or f"{employee_id.lower()}@example.com"
            first_name = document.get("first_name", "")
            last_name = document.get("last_name", "")

            user = None
            if email:
                user = User.objects.filter(email=email).first()
            if not user:
                username_candidate = email.split("@")[0] if email else employee_id.lower()
                username = get_username(username_candidate)
                user = User.objects.create_user(username=username, email=email, password=DEFAULT_PASSWORD)
            elif not user.username:
                user.username = get_username(employee_id.lower())
                user.set_password(DEFAULT_PASSWORD)
                user.save()

            employee, created_flag = Employee.objects.get_or_create(
                employee_id=employee_id,
                defaults={
                    "user": user,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "gender": document.get("gender", ""),
                    "date_of_birth": document.get("date_of_birth"),
                    "hire_date": document.get("hire_date"),
                    "department": document.get("department", ""),
                    "role": document.get("role", ""),
                    "salary": normalize_salary(document.get("salary")),
                    "phone": as_str(document.get("phone")),
                    "address": document.get("address", ""),
                    "city": document.get("city", ""),
                    "state": document.get("state", ""),
                    "postal_code": as_str(document.get("postal_code")),
                    "manager_id": as_str(document.get("manager_id")),
                    "full_time": bool(document.get("full_time", True)),
                    "status": document.get("status", ""),
                    "performance_score": normalize_score(document.get("performance_score")),
                    "emergency_contact_name": document.get("emergency_contact_name", ""),
                    "emergency_contact_phone": as_str(document.get("emergency_contact_phone")),
                    "bank_account_masked": document.get("bank_account_masked", ""),
                }
            )

            if created_flag:
                created += 1
            else:
                employee.user = user
                employee.first_name = first_name
                employee.last_name = last_name
                employee.email = email
                employee.gender = document.get("gender", "")
                employee.date_of_birth = document.get("date_of_birth")
                employee.hire_date = document.get("hire_date")
                employee.department = document.get("department", "")
                employee.role = document.get("role", "")
                employee.salary = normalize_salary(document.get("salary"))
                employee.phone = as_str(document.get("phone"))
                employee.address = document.get("address", "")
                employee.city = document.get("city", "")
                employee.state = document.get("state", "")
                employee.postal_code = as_str(document.get("postal_code"))
                employee.manager_id = as_str(document.get("manager_id"))
                employee.full_time = bool(document.get("full_time", True))
                employee.status = document.get("status", "")
                employee.performance_score = normalize_score(document.get("performance_score"))
                employee.emergency_contact_name = document.get("emergency_contact_name", "")
                employee.emergency_contact_phone = as_str(document.get("emergency_contact_phone"))
                employee.bank_account_masked = document.get("bank_account_masked", "")
                employee.save()
                updated += 1

    client.close()
    print(f"Employees created: {created}")
    print(f"Employees updated: {updated}")


if __name__ == "__main__":
    import_employees()
