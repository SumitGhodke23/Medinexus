from django.db import models
from patients.models import Patients


class Bed(models.Model):

    BED_TYPES = [
        ("General", "General"),
        ("Semi-Private", "Semi-Private"),
        ("Private", "Private"),
        ("ICU", "ICU"),
        ("Emergency", "Emergency"),
    ]

    BED_STATUS = [
        ("Available", "Available"),
        ("Occupied", "Occupied"),
        ("Maintenance", "Maintenance"),
    ]

    bed_id = models.AutoField(primary_key=True)

    bed_number = models.CharField(
        max_length=50,
        unique=True
    )

    room_number = models.CharField(
        max_length=50
    )

    ward_name = models.CharField(
        max_length=100
    )

    bed_type = models.CharField(
        max_length=30,
        choices=BED_TYPES,
        default="General"
    )

    status = models.CharField(
        max_length=30,
        choices=BED_STATUS,
        default="Available"
    )

    patient = models.ForeignKey(
        Patients,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_beds"
    )

    admission_date = models.DateField(
        null=True,
        blank=True
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.bed_number} - {self.ward_name}"