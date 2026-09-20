from django.db import models
from patients.models import Patients
from doctors.models import Doctor


class Appointment(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Rescheduled', 'Rescheduled'),
    ]

    appointment_id = models.AutoField(primary_key=True)

    patient = models.ForeignKey(
        Patients,
        on_delete=models.CASCADE
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE
    )

    appointment_date = models.DateField()

    appointment_time = models.TimeField()

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    queue_token = models.PositiveIntegerField(null=True, blank=True)
    estimated_wait_minutes = models.PositiveIntegerField(default=0)
    cancellation_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("doctor", "appointment_date", "appointment_time"),
                condition=models.Q(status__in=("Pending", "Confirmed", "Rescheduled")),
                name="unique_active_doctor_slot",
            ),
        ]

    def __str__(self):
        return f"{self.patient.full_name} - {self.doctor.full_name}"