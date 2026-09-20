from django.contrib import admin
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):

    list_display = (
        'doctor_id',
        'full_name',
        'specialization',
        'education',
        'experience',
        'phone',
        'available',
        'user',
    )

    search_fields = (
        'full_name',
        'specialization',
        'education',
        'phone',
    )

    list_filter = (
        'specialization',
        'available',
        'department',
    )