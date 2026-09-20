from django.contrib import admin
from .models import Bill


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = (
        "bill_id",
        "patient",
        "total_amount",
        "payment_status",
        "bill_date",
    )

    search_fields = (
        "patient__name",
    )

    list_filter = (
        "payment_status",
        "bill_date",
    )

    readonly_fields = (
        "total_amount",
        "bill_date",
    )