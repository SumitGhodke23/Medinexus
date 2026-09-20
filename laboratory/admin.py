from django.contrib import admin
from .models import LaboratoryTest


@admin.register(LaboratoryTest)
class LaboratoryTestAdmin(admin.ModelAdmin):

    list_display = (
        "test_id",
        "patient",
        "doctor",
        "test_name",
        "status",
        "test_date",
    )

    search_fields = (
        "test_name",
        "patient__name",
        "doctor__name",
    )

    list_filter = (
        "status",
        "test_date",
    )

    readonly_fields = (
        "test_date",
    )