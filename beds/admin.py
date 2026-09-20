from django.contrib import admin
from .models import Bed


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):

    list_display = (
        "bed_id",
        "bed_number",
        "room_number",
        "ward_name",
        "bed_type",
        "status",
        "patient",
    )

    search_fields = (
        "bed_number",
        "room_number",
        "ward_name",
        "patient__name",
    )

    list_filter = (
        "bed_type",
        "status",
        "ward_name",
    )