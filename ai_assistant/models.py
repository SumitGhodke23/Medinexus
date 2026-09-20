from django.db import models
from patients.models import Patients


class ChatMessage(models.Model):

    MESSAGE_TYPE = [
        ("User", "User"),
        ("AI", "AI"),
    ]

    message_id = models.AutoField(primary_key=True)

    patient = models.ForeignKey(
        Patients,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chat_messages"
    )

    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPE
    )

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.message_type} - {self.created_at}"