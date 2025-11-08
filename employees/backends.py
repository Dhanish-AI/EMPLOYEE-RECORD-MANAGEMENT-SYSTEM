from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmployeeIdentifierBackend(ModelBackend):
    """Authenticate using username, email, or linked employee ID."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        identifier = username or kwargs.get("email") or kwargs.get("identifier")
        if not identifier or not password:
            return None

        identifier = str(identifier).strip()
        UserModel = get_user_model()

        user = (
            UserModel.objects.select_related("employee_profile")
            .filter(
                Q(username__iexact=identifier)
                | Q(email__iexact=identifier)
                | Q(employee_profile__employee_id__iexact=identifier)
            )
            .first()
        )

        if not user:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
