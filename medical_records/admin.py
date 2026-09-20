from django.contrib import admin
from .models import MedicalRecord


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):

    list_display = (
        "record_id",
        "patient",
        "doctor",
        "disease",
        "record_date",
    )

    list_filter = (
        "record_date",
        "disease",
    )

    search_fields = (
        "patient__name",
        "disease",
        "diagnosis",
    )