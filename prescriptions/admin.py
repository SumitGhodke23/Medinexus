from django.contrib import admin
from .models import Prescription


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):

    list_display = (
        "prescription_id",
        "patient",
        "doctor",
        "medicine_name",
        "dosage",
        "frequency",
        "duration",
        "prescribed_date",
    )

    list_filter = (
        "frequency",
        "prescribed_date",
    )

    search_fields = (
        "patient__name",
        "medicine_name",
        "doctor__name",
    )