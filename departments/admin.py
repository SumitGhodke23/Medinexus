from django.contrib import admin
from .models import Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):

    list_display = (
        "department_id",
        "department_name",
        "department_code",
        "head_of_department",
        "contact_number",
        "status",
        "created_at",
    )

    search_fields = (
        "department_name",
        "department_code",
        "head_of_department",
    )

    list_filter = (
        "status",
        "created_at",
    )

    readonly_fields = (
        "created_at",
    )