from django.contrib import admin
from .models import Patients


@admin.register(Patients)
class PatientsAdmin(admin.ModelAdmin):
    list_display = (
        'patient_id',
        'full_name',
        'phone',
        'blood_group',
        'disease',
        'created_at',
        'user',
    )

    search_fields = (
        'full_name',
        'phone',
        'email',
    )

    list_filter = (
        'blood_group',
        'gender',
    )