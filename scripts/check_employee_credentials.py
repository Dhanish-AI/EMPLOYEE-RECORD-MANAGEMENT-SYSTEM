import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "erms_project.settings")

import django

from django.db.models import Q

try:
    django.setup()
except Exception as exc:  # pragma: no cover
    sys.stderr.write(f"Failed to set up Django: {exc}\n")
    sys.exit(1)

from django.contrib.auth import get_user_model  # noqa: E402

User = get_user_model()


def inspect(identifier: str) -> None:
    match = (
        User.objects.select_related("employee_profile")
        .filter(
            Q(username__iexact=identifier)
            | Q(email__iexact=identifier)
            | Q(employee_profile__employee_id__iexact=identifier)
        )
        .first()
    )
    if not match:
        print(f"No user found for identifier '{identifier}'")
        return

    profile = getattr(match, "employee_profile", None)
    employee_id = getattr(profile, "employee_id", None)
    print(f"Match found -> username={match.username}, email={match.email}, employee_id={employee_id}")
    for test_password in ("Employee123!", "TempEmp456!", "TestPass123!", "AdminPass123!"):
        print(f"  Password '{test_password}': {match.check_password(test_password)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/check_employee_credentials.py <identifier>")
        sys.exit(1)

    inspect(sys.argv[1])
