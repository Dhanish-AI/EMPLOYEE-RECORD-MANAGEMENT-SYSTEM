"""
URL configuration for erms_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from employees import views as employee_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', employee_views.home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('auth/admin/', employee_views.admin_login, name='admin_login'),
    path('auth/employee/', employee_views.employee_login, name='employee_login'),
    path('auth/logout/', employee_views.logout_view, name='logout'),
    path('dashboard/admin/', employee_views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/employee/', employee_views.employee_dashboard, name='employee_dashboard'),
    path('employees/add/', employee_views.employee_create, name='employee_create'),
    path('employees/<int:pk>/', employee_views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', employee_views.employee_update, name='employee_update'),
    path('employees/<int:pk>/delete/', employee_views.employee_delete, name='employee_delete'),
    path('employees/search/', employee_views.admin_employee_search, name='admin_employee_search'),
    path('account/password/', employee_views.employee_change_password, name='employee_change_password'),
]
