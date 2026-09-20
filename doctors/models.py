from django.db import models


class Doctor(models.Model):
    doctor_id = models.AutoField(primary_key=True)

    full_name = models.CharField(max_length=100)

    specialization = models.CharField(max_length=100)

    education = models.CharField(max_length=255)

    experience = models.PositiveIntegerField(
        help_text="Experience in years"
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    photo = models.ImageField(
        upload_to="doctors/",
        blank=True,
        null=True
    )

    available = models.BooleanField(default=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.full_name
    
    department = models.ForeignKey(
    "departments.Department",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="doctors"
)