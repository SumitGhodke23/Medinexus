from django.conf import settings
from django.core.mail import send_mail

from .models import Notification


def notify(user, kind, title, message, subject=None):
	if not user:
		return
	Notification.objects.create(user=user, kind=kind, title=title, message=message)
	if user.email:
		send_mail(
			subject or title,
			message,
			settings.DEFAULT_FROM_EMAIL,
			[user.email],
			fail_silently=True,
		)