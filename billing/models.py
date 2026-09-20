from django.db import models
from patients.models import Patients


class Bill(models.Model):
    PAYMENT_STATUS = [
        ("Pending", "Pending"),
        ("Paid", "Paid"),
        ("Partially Paid", "Partially Paid"),
    ]

    bill_id = models.AutoField(primary_key=True)

    patient = models.ForeignKey(
        Patients,
        on_delete=models.CASCADE,
        related_name="bills"
    )

    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    medicine_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    laboratory_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    room_charges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    other_charges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    payment_status = models.CharField(
        max_length=30,
        choices=PAYMENT_STATUS,
        default="Pending"
    )

    bill_date = models.DateField(auto_now_add=True)

    notes = models.TextField(
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        self.total_amount = (
            self.consultation_fee
            + self.medicine_fee
            + self.laboratory_fee
            + self.room_charges
            + self.other_charges
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Bill {self.bill_id} - {self.patient}"