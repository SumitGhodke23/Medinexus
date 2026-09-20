from django.contrib import admin
from .models import Medicine


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
	list_display = ("medicine_name", "category", "quantity", "unit_price", "expiry_date", "active")
	list_filter = ("active", "category")
	search_fields = ("medicine_name", "supplier")
