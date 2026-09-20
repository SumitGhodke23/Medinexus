from django.db import models
from patients.models import Patients
from doctors.models import Doctor
from medical_records.models import MedicalRecord


class Prescription(models.Model):

    prescription_id = models.AutoField(primary_key=True)

    patient = models.ForeignKey(
        Patients,
        on_delete=models.CASCADE,
        related_name="prescriptions"
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prescriptions_given"
    )

    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prescriptions"
    )

    medicine_name = models.CharField(max_length=200)

    dosage = models.CharField(
        max_length=100,
        help_text="Example: 1 tablet"
    )

    frequency = models.CharField(
        max_length=100,
        help_text="Example: Twice a day"
    )

    duration = models.CharField(
        max_length=100,
        help_text="Example: 5 days"
    )

    instructions = models.TextField(blank=True)

    prescribed_date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.patient} - {self.medicine_name}"