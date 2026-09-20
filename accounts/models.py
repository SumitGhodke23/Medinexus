from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
	ROLE_CHOICES = (
		("patient", "Patient"),
		("doctor", "Doctor"),
		("admin", "Administrator"),
	)

	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
	role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="patient")

	def __str__(self):
		return f"{self.user.username} ({self.get_role_display()})"


class Notification(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
	kind = models.CharField(max_length=40)
	title = models.CharField(max_length=200)
	message = models.TextField()
	read_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ("-created_at",)

	def __str__(self):
		return f"{self.user.username}: {self.title}"

# Create your models here.
