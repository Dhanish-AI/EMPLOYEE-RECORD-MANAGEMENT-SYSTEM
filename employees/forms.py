from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

from .models import Employee

User = get_user_model()

DEPARTMENT_OPTIONS = [
    "Administration",
    "Customer Support",
    "Engineering",
    "Finance",
    "Human Resources",
    "Information Technology",
    "Legal",
    "Operations",
    "Product",
    "Sales",
]

ROLE_OPTIONS = [
    "Accountant",
    "Business Analyst",
    "Customer Success Manager",
    "Data Analyst",
    "Finance Manager",
    "HR Executive",
    "HR Manager",
    "Operations Executive",
    "Operations Manager",
    "Product Manager",
    "Software Engineer",
    "Software Lead",
    "Support Specialist",
]

CITY_OPTIONS = [
   "Ariyalur",
"Chengalpattu",
"Chennai",
"Coimbatore",
"Cuddalore",
"Dharmapuri",
"Dindigul",
"Erode",
"Kallakurichi",
"Kanchipuram",
"Kanyakumari",
"Karur",
"Krishnagiri",
"Madurai",
"Mayiladuthurai",
"Nagapattinam",
"Namakkal",
"Perambalur",
"Pudukkottai",
"Ramanathapuram",
"Ranipet",
"Salem",
"Sivagangai",
"Tenkasi",
"Thanjavur",
"Theni",
"Thoothukudi",
"Tiruchirappalli",
"Tirunelveli",
"Tirupattur",
"Tiruppur",
"Tiruvallur",
"Tiruvannamalai",
"Tiruvarur",
"Vellore",
"Viluppuram",
"Virudhunagar",
"The Nilgiris",

]

STATE_OPTIONS = [
    "Andhra Pradesh",
"Arunachal Pradesh",
"Assam",
"Bihar",
"Chhattisgarh",
"Goa",
"Gujarat",
"Haryana",
"Himachal Pradesh",
"Jharkhand",
"Karnataka",
"Kerala",
"Madhya Pradesh",
"Maharashtra",
"Manipur",
"Meghalaya",
"Mizoram",
"Nagaland",
"Odisha",
"Punjab",
"Rajasthan",
"Sikkim",
"Tamil Nadu",
"Telangana",
"Tripura",
"Uttar Pradesh",
"Uttarakhand",
"West Bengal",
"Andaman and Nicobar Islands",
"Chandigarh",
"Dadra and Nagar Haveli and Daman and Diu",
"Delhi",
"Jammu and Kashmir",
"Ladakh",
"Lakshadweep",
"Puducherry",

]

STATUS_OPTIONS = [
    "Active",
    "Contract",
    "On Leave",
    "Probation",
    "Retired",
    "Terminated",
]

GENDER_OPTIONS = [
    "Female",
    "Male",
    "Non-Binary",
    "Prefer not to say",
]

SELECT_OPTIONS = {
    "department": DEPARTMENT_OPTIONS,
    "role": ROLE_OPTIONS,
    "city": CITY_OPTIONS,
    "state": STATE_OPTIONS,
    "status": STATUS_OPTIONS,
    "gender": GENDER_OPTIONS,
}

FULL_TIME_CHOICES = [
    ("1", "Yes"),
    ("0", "No"),
]


class AdminLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise forms.ValidationError("You do not have admin access.", code="no_admin_access")


class EmployeeLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.is_staff:
            raise forms.ValidationError("Please use the admin login.", code="admin_redirect")
        if not hasattr(user, "employee_profile"):
            raise forms.ValidationError("Employee record not found.", code="no_profile")


class EmployeeForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    hire_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "first_name",
            "last_name",
            "email",
            "gender",
            "date_of_birth",
            "hire_date",
            "department",
            "role",
            "salary",
            "phone",
            "address",
            "city",
            "state",
            "postal_code",
            "manager_id",
            "full_time",
            "status",
            "performance_score",
            "emergency_contact_name",
            "emergency_contact_phone",
            "bank_account_masked",
        ]
        widgets = {
            "salary": forms.NumberInput(attrs={"step": "0.01"}),
            "performance_score": forms.NumberInput(attrs={"min": 0}),
            "full_time": forms.CheckboxInput(attrs={"class": "checkbox"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        full_time_label = self.fields["full_time"].label
        full_time_initial_raw = self.initial.get("full_time")
        if full_time_initial_raw is None:
            if self.instance and getattr(self.instance, "full_time", None) is not None:
                full_time_current = bool(self.instance.full_time)
            else:
                full_time_current = True
        else:
            full_time_current = str(full_time_initial_raw).lower() in {"1", "true", "yes", "on"}

        self.fields["full_time"] = forms.TypedChoiceField(
            label=full_time_label,
            choices=FULL_TIME_CHOICES,
            coerce=lambda value: str(value).lower() in {"1", "true", "yes", "on"},
            widget=forms.RadioSelect(attrs={"class": "radio-toggle"}),
            initial="1" if full_time_current else "0",
        )

        self.select_fields = set()
        self.radio_fields = {"full_time"}

        for name, field in self.fields.items():
            if name == "full_time":
                continue
            if name in SELECT_OPTIONS:
                options = list(SELECT_OPTIONS[name])
                initial_value = self.initial.get(name)
                if not initial_value and self.instance and getattr(self.instance, name, None):
                    initial_value = getattr(self.instance, name)
                if initial_value and initial_value not in options:
                    options.insert(0, initial_value)

                choices = [("", f"Select {field.label}")]
                choices.extend((option, option) for option in options)
                field.widget = forms.Select(choices=choices)
                field.widget.attrs.setdefault("class", "input select")
                self.select_fields.add(name)
            elif getattr(field.widget, "input_type", "") == "checkbox":
                field.widget.attrs.setdefault("class", "checkbox")
            else:
                field.widget.attrs.setdefault("class", "input")
                field.widget.attrs.setdefault("placeholder", field.label)


class EmployeeCreateForm(EmployeeForm):
    username = forms.CharField(max_length=150)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")
        if password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        if not password1:
            raise forms.ValidationError("Password is required.")
        return cleaned

    def save(self, commit=True):
        employee = super().save(commit=False)
        username = self.cleaned_data["username"].strip()
        password = self.cleaned_data["password1"]
        email = self.cleaned_data["email"]
        user = User.objects.create_user(username=username, password=password, email=email)
        user.is_staff = False
        user.save()
        employee.user = user
        if commit:
            employee.save()
            self.save_m2m()
        return employee


class EmployeeUpdateForm(EmployeeForm):
    username = forms.CharField(max_length=150)
    password1 = forms.CharField(label="New Password", widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["username"].initial = self.instance.user.username
        else:
            self.fields["username"].initial = ""

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if not username:
            raise forms.ValidationError("Username is required.")
        qs = User.objects.filter(username=username)
        if self.instance.user:
            qs = qs.exclude(pk=self.instance.user.pk)
        if qs.exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")
        if password1 or password2:
            if password1 != password2:
                self.add_error("password2", "Passwords do not match.")
        else:
            if not self.instance.user:
                self.add_error("password1", "Password is required to create a login.")
        return cleaned

    def save(self, commit=True):
        employee = super().save(commit=False)
        username = self.cleaned_data["username"].strip()
        password = self.cleaned_data.get("password1")
        email = self.cleaned_data["email"]

        user = employee.user
        if user:
            user.username = username
            user.email = email
            if password:
                user.set_password(password)
            user.is_staff = False
            user.save()
        else:
            user = User.objects.create_user(username=username, password=password, email=email)
            user.is_staff = False
            user.save()
            employee.user = user

        if commit:
            employee.save()
            self.save_m2m()
        return employee
