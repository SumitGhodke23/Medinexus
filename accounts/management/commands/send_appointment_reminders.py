from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from appointments.models import Appointment
from accounts.services import notify


class Command(BaseCommand):
    help = "Send one-day reminders for upcoming confirmed appointments."

    def handle(self, *args, **options):
        now = timezone.localtime()
        window_start = now + timedelta(hours=23)
        window_end = now + timedelta(hours=25)
        sent = 0
        appointments = Appointment.objects.filter(status="Confirmed").select_related("patient", "doctor")
        for appointment in appointments:
            appointment_at = timezone.make_aware(
                datetime.combine(appointment.appointment_date, appointment.appointment_time),
                timezone.get_current_timezone(),
            )
            if window_start <= appointment_at <= window_end:
                notify(
                    appointment.patient.user,
                    "appointment_reminder",
                    "Appointment reminder",
                    f"Reminder: appointment #{appointment.appointment_id} with Dr. {appointment.doctor.full_name} is tomorrow at {appointment.appointment_time}.",
                )
                sent += 1
        self.stdout.write(self.style.SUCCESS(f"Sent {sent} appointment reminder(s)."))
