from django.db import models
from django.contrib.auth.models import User


class Patients(models.Model):
    patient_id = models.AutoField(primary_key=True)

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patient_record",
    )

    full_name = models.CharField(max_length=100)

    email = models.EmailField(
        max_length=100,
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    gender = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    blood_group = models.CharField(
        max_length=5,
        blank=True,
        null=True
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    disease = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "patients"

    def __str__(self):
        return self.full_name