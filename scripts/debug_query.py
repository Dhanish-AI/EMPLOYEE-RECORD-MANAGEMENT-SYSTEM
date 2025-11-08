import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "erms_project.settings")

import django

django.setup()

from employees.models import Employee

print("Total employees:", Employee.objects.count())
print("Full-time count:", Employee.objects.filter(full_time=True).count())
print("Sample departments:", list(Employee.objects.values_list("department", flat=True)[:5]))
