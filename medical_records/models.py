from django.db import models
from patients.models import Patients
from doctors.models import Doctor


class MedicalRecord(models.Model):

    record_id = models.AutoField(primary_key=True)

    patient = models.ForeignKey(
        Patients,
        on_delete=models.CASCADE,
        related_name="patient_medical_records"
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="doctor_medical_records"
    )

    disease = models.CharField(max_length=200)

    symptoms = models.TextField(blank=True)

    diagnosis = models.TextField(blank=True)

    treatment = models.TextField(blank=True)

    prescription = models.TextField(blank=True)

    blood_pressure = models.CharField(
        max_length=30,
        blank=True
    )

    temperature = models.CharField(
        max_length=30,
        blank=True
    )

    record_date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.patient} - {self.disease}"