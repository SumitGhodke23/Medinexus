from django.db import models
from patients.models import Patients
from doctors.models import Doctor


class LaboratoryTest(models.Model):

    TEST_STATUS = [
        ("Requested", "Requested"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    test_id = models.AutoField(primary_key=True)

    patient = models.ForeignKey(
        Patients,
        on_delete=models.CASCADE,
        related_name="laboratory_tests"
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="laboratory_tests"
    )

    test_name = models.CharField(
        max_length=255
    )

    test_result = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=30,
        choices=TEST_STATUS,
        default="Requested"
    )

    test_date = models.DateField(
        auto_now_add=True
    )

    technician_notes = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.patient} - {self.test_name}"