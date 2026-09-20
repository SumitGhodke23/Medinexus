from django.db import models


class Department(models.Model):

    department_id = models.AutoField(primary_key=True)

    department_name = models.CharField(
        max_length=150,
        unique=True
    )

    department_code = models.CharField(
        max_length=20,
        unique=True
    )

    head_of_department = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    contact_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    status = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.department_name