from django.conf import settings
from django.db import models


class Employee(models.Model):
    employee_id = models.CharField(max_length=20, unique=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="employee_profile")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    hire_date = models.DateField()
    department = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    manager_id = models.CharField(max_length=20, blank=True)
    full_time = models.BooleanField(default=True)
    status = models.CharField(max_length=50)
    performance_score = models.IntegerField(default=0)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=20)
    bank_account_masked = models.CharField(max_length=30)

    class Meta:
        ordering = ["employee_id"]

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self) -> str:
        return f"{self.employee_id} - {self.full_name}"
