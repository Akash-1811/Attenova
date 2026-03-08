from django.urls import path
from Employee.views import (
    EmployeeView,
    designation_list,
    employee_export,
    employee_import,
    check_employee_duplicate,
    create_employee_with_login,
)

urlpatterns = [
    path("designations/", designation_list, name="employee-designations"),
    path("check-duplicate/", check_employee_duplicate, name="employee-check-duplicate"),
    path("create-with-login/", create_employee_with_login, name="employee-create-with-login"),
    path("import/", employee_import, name="employee-import"),
    path("export/", employee_export, name="employee-export"),
    path("", EmployeeView.as_view(), name="employee-list-create"),
    path("<int:pk>/", EmployeeView.as_view(), name="employee-detail"),
]
