from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.db.models import Count, Q
from django.utils import timezone
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import AdminLoginForm, EmployeeCreateForm, EmployeeLoginForm, EmployeeUpdateForm
from .models import Employee


def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff, login_url="admin_login")(view_func)


def employee_required(view_func):
    def check(user):
        return user.is_authenticated and not user.is_staff and hasattr(user, "employee_profile")

    return user_passes_test(check, login_url="employee_login")(view_func)


def redirect_authenticated_user(user):
    if user.is_staff:
        return reverse("admin_dashboard")
    if hasattr(user, "employee_profile"):
        return reverse("employee_dashboard")
    return None


def login_view(request: HttpRequest, form_class: type[AuthenticationForm], template: str, role: str) -> HttpResponse:
    if request.user.is_authenticated:
        redirect_url = redirect_authenticated_user(request.user)
        if redirect_url:
            return redirect(redirect_url)

    form = form_class(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            redirect_url = redirect_authenticated_user(user)
            return redirect(redirect_url or "home")

    return render(
        request,
        template,
        {
            "form": form,
            "role": role,
        },
    )


def admin_login(request: HttpRequest) -> HttpResponse:
    return login_view(request, AdminLoginForm, "registration/login.html", role="admin")


def employee_login(request: HttpRequest) -> HttpResponse:
    return login_view(request, EmployeeLoginForm, "registration/login.html", role="employee")


def logout_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out.")
    return redirect("home")


def home(request: HttpRequest) -> HttpResponse:
    redirect_url = redirect_authenticated_user(request.user)
    if redirect_url:
        return redirect(redirect_url)
    return render(request, "home.html")


@admin_required
def admin_dashboard(request: HttpRequest) -> HttpResponse:
    base_qs = Employee.objects.all()
    all_employees = list(base_qs)
    total_employees = len(all_employees)
    full_time_count = sum(1 for employee in all_employees if employee.full_time)
    department_count = len({employee.department for employee in all_employees if employee.department})

    query = request.GET.get("q", "").strip()
    employees_qs = base_qs
    if query:
        employees_qs = employees_qs.filter(
            Q(employee_id__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
            | Q(department__icontains=query)
            | Q(role__icontains=query)
        )

    employees = employees_qs.order_by("employee_id")

    show_all = request.GET.get("view") == "all"
    preview_limit = 8
    displayed_employees = employees if show_all else employees[:preview_limit]

    today = timezone.now().date()

    def to_float(value):
        if value is None:
            return None
        if hasattr(value, "to_decimal"):
            value = value.to_decimal()
        if isinstance(value, Decimal):
            return float(value)
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    salaries = [to_float(employee.salary) for employee in all_employees if to_float(employee.salary) is not None]
    tenures = [
        max((today - employee.hire_date).days / 365.25, 0)
        for employee in all_employees
        if employee.hire_date
    ]
    average_salary = round(sum(salaries) / len(salaries), 2) if salaries else 0
    average_tenure = round(sum(tenures) / len(tenures), 1) if tenures else 0

    department_metrics: dict[str, dict[str, float]] = {}
    for employee in all_employees:
        department = employee.department or "Unassigned"
        stats = department_metrics.setdefault(
            department,
            {"count": 0, "salary_total": 0.0, "tenure_total": 0.0},
        )
        stats["count"] += 1
        salary_value = to_float(employee.salary)
        if salary_value is not None:
            stats["salary_total"] += salary_value
        if employee.hire_date:
            tenure_years = max((today - employee.hire_date).days / 365.25, 0)
            stats["tenure_total"] += tenure_years

    sorted_departments = sorted(department_metrics.items(), key=lambda item: item[1]["count"], reverse=True)
    top_departments = sorted_departments[:6]

    department_salary_chart = {
        "labels": [dept for dept, _ in top_departments],
        "values": [
            round((stats["salary_total"] / stats["count"]) if stats["count"] else 0, 2)
            for _, stats in top_departments
        ],
    }
    department_tenure_chart = {
        "labels": [dept for dept, _ in top_departments],
        "values": [
            round((stats["tenure_total"] / stats["count"]) if stats["count"] else 0, 1)
            for _, stats in top_departments
        ],
    }

    department_breakdown = (
        base_qs.values("department")
        .order_by("department")
        .annotate(total=Count("id"))
    )
    status_breakdown = (
        base_qs.values("status")
        .order_by("status")
        .annotate(total=Count("id"))
    )

    department_chart = {
        "labels": [item["department"] or "Unassigned" for item in department_breakdown],
        "values": [item["total"] for item in department_breakdown],
    }
    status_chart = {
        "labels": [item["status"] or "Unknown" for item in status_breakdown],
        "values": [item["total"] for item in status_breakdown],
    }

    context = {
        "employees": employees,
        "displayed_employees": displayed_employees,
        "employees_count": total_employees,
        "full_time_count": full_time_count,
        "department_count": department_count,
        "query": query,
        "show_all_employees": show_all,
        "preview_limit": preview_limit,
        "department_chart": department_chart,
        "status_chart": status_chart,
        "department_salary_chart": department_salary_chart,
        "department_tenure_chart": department_tenure_chart,
        "average_salary": average_salary,
        "average_tenure": average_tenure,
    }
    return render(request, "employees/admin_dashboard.html", context)


@admin_required
def admin_employee_search(request: HttpRequest) -> JsonResponse:
    query = request.GET.get("q", "").strip()
    employees_qs = Employee.objects.all()
    if query:
        employees_qs = employees_qs.filter(
            Q(employee_id__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
            | Q(department__icontains=query)
            | Q(role__icontains=query)
        )

    employees = employees_qs.order_by("employee_id")[:50]
    results = [
        {
            "id": employee.pk,
            "employee_id": employee.employee_id,
            "name": employee.full_name,
            "role": employee.role,
            "department": employee.department,
            "status": employee.status,
            "hire_date": employee.hire_date.strftime("%b %d, %Y"),
            "detail_url": reverse("employee_detail", args=[employee.pk]),
            "edit_url": reverse("employee_update", args=[employee.pk]),
            "delete_url": reverse("employee_delete", args=[employee.pk]),
        }
        for employee in employees
    ]

    return JsonResponse({"results": results})


@employee_required
def employee_dashboard(request: HttpRequest) -> HttpResponse:
    employee = request.user.employee_profile
    return render(request, "employees/employee_dashboard.html", {"employee": employee})


@employee_required
def employee_change_password(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been updated successfully.")
            return redirect("employee_dashboard")
    else:
        form = PasswordChangeForm(request.user)

    return render(
        request,
        "employees/employee_change_password.html",
        {
            "form": form,
        },
    )


@admin_required
def employee_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = EmployeeCreateForm(request.POST)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f"Employee {employee.full_name} was created successfully.")
            return redirect("admin_dashboard")
    else:
        form = EmployeeCreateForm()

    return render(
        request,
        "employees/employee_form.html",
        {
            "form": form,
            "title": "Add Employee",
            "submit_label": "Create Employee",
        },
    )


@admin_required
def employee_update(request: HttpRequest, pk: int) -> HttpResponse:
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        form = EmployeeUpdateForm(request.POST, instance=employee)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f"Employee {employee.full_name} was updated successfully.")
            return redirect("employee_detail", pk=employee.pk)
    else:
        form = EmployeeUpdateForm(instance=employee)

    return render(
        request,
        "employees/employee_form.html",
        {
            "form": form,
            "title": "Edit Employee",
            "submit_label": "Save Changes",
            "employee": employee,
        },
    )


@admin_required
def employee_detail(request: HttpRequest, pk: int) -> HttpResponse:
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, "employees/employee_detail.html", {"employee": employee})


@admin_required
def employee_delete(request: HttpRequest, pk: int) -> HttpResponse:
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        full_name = employee.full_name
        user = employee.user
        employee.delete()
        if user:
            user.delete()
        messages.success(request, f"Employee {full_name} was deleted successfully.")
        return redirect("admin_dashboard")

    return render(
        request,
        "employees/employee_confirm_delete.html",
        {
            "employee": employee,
        },
    )
