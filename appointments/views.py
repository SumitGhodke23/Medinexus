from datetime import datetime, timedelta

from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from patients.models import Patients
from doctors.models import Doctor
from .models import Appointment
from accounts.permissions import role_required, user_role
from accounts.services import notify


ACTIVE_STATUSES = ("Pending", "Confirmed", "Rescheduled")


def available_slots(doctor, appointment_date):
    start = datetime.combine(appointment_date, doctor.availability_start)
    end = datetime.combine(appointment_date, doctor.availability_end)
    booked = set(Appointment.objects.filter(
        doctor=doctor,
        appointment_date=appointment_date,
        status__in=ACTIVE_STATUSES,
    ).values_list("appointment_time", flat=True))
    slots = []
    current = start
    while current < end:
        if current.time() not in booked:
            slots.append(current.strftime("%H:%M"))
        current += timedelta(minutes=doctor.slot_duration_minutes)
    return slots


@role_required("admin", "patient", "doctor")
def appointment_list(request):
    appointments = Appointment.objects.select_related(
        "patient",
        "doctor"
    ).order_by("-appointment_date", "-appointment_time")
    role = user_role(request.user)
    if role == "patient":
        appointments = appointments.filter(patient__user=request.user)
    elif role == "doctor":
        appointments = appointments.filter(doctor__user=request.user)

    return render(
        request,
        "appointments/appointment_list.html",
        {"appointments": appointments, "role": role}
    )


@role_required("admin", "patient")
def appointment_add(request):
    if request.method == "POST":
        patient_id = request.POST.get("patient")
        doctor_id = request.POST.get("doctor")
        appointment_date = request.POST.get("appointment_date")
        appointment_time = request.POST.get("appointment_time")
        reason = request.POST.get("reason")

        if not all((patient_id, doctor_id, appointment_date, appointment_time, reason)):
            messages.error(request, "Complete all appointment fields.")
        else:
            patient = Patients.objects.filter(user=request.user).first() if user_role(request.user) == "patient" else Patients.objects.filter(pk=patient_id).first()
            if not patient:
                messages.error(request, "Your account is not linked to a patient record yet. Contact hospital administration.")
                return redirect("appointment_add")
            doctor = get_object_or_404(Doctor, pk=doctor_id, available=True)
            try:
                with transaction.atomic():
                    date_value = datetime.strptime(appointment_date, "%Y-%m-%d").date()
                    time_value = datetime.strptime(appointment_time, "%H:%M").time()
                    if appointment_time not in available_slots(doctor, date_value):
                        messages.error(request, "That appointment slot is no longer available.")
                        return redirect("appointment_add")
                    last_token = Appointment.objects.filter(
                        doctor=doctor,
                        appointment_date=date_value,
                        status__in=ACTIVE_STATUSES,
                    ).order_by("-queue_token").values_list("queue_token", flat=True).first() or 0
                    appointment = Appointment.objects.create(
                        patient=patient,
                        doctor=doctor,
                        appointment_date=date_value,
                        appointment_time=time_value,
                        reason=reason,
                        queue_token=last_token + 1,
                        estimated_wait_minutes=last_token * doctor.slot_duration_minutes,
                    )
            except (ValueError, IntegrityError):
                messages.error(request, "That slot was just booked. Please choose another time.")
                return redirect("appointment_add")
            notify(
                patient.user,
                "appointment_booked",
                "Appointment booked",
                f"Appointment #{appointment.appointment_id} with Dr. {doctor.full_name} is booked for {appointment.appointment_date} at {appointment.appointment_time}. Token {appointment.queue_token}.",
            )
            notify(
                doctor.user,
                "appointment_booked",
                "New appointment assigned",
                f"Appointment #{appointment.appointment_id} with {patient.full_name} is booked for {appointment.appointment_date} at {appointment.appointment_time}.",
            )
            messages.success(request, "Appointment created successfully.")
            return redirect("appointment_list")

    selected_date = request.GET.get("date")
    selected_doctor = request.GET.get("doctor")
    slots = []
    if selected_date and selected_doctor:
        try:
            date_value = datetime.strptime(selected_date, "%Y-%m-%d").date()
            doctor = Doctor.objects.filter(pk=selected_doctor, available=True).first()
            if doctor:
                slots = available_slots(doctor, date_value)
        except ValueError:
            slots = []
    return render(
        request,
        "appointments/appointment_add.html",
        {
            "patients": Patients.objects.filter(user=request.user) if user_role(request.user) == "patient" else Patients.objects.order_by("full_name"),
            "doctors": Doctor.objects.filter(available=True).order_by("full_name"),
            "available_slots": slots,
        },
    )


@role_required("admin", "patient", "doctor")
def appointment_action(request, appointment_id, action):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    role = user_role(request.user)
    owns = appointment.patient.user_id == request.user.id or appointment.doctor.user_id == request.user.id
    if role != "admin" and not owns:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    if request.method != "POST":
        return redirect("appointment_list")
    if action == "cancel" and appointment.status not in ("Completed", "Cancelled"):
        appointment.status = "Cancelled"
        appointment.cancellation_reason = request.POST.get("reason", "Cancelled by user")
        appointment.save(update_fields=("status", "cancellation_reason", "updated_at"))
        notify(appointment.patient.user, "appointment_cancelled", "Appointment cancelled", f"Appointment #{appointment.appointment_id} was cancelled.")
    elif action == "reschedule" and appointment.status not in ("Completed", "Cancelled"):
        try:
            new_date = datetime.strptime(request.POST.get("appointment_date", ""), "%Y-%m-%d").date()
            new_time = datetime.strptime(request.POST.get("appointment_time", ""), "%H:%M").time()
            if request.POST.get("appointment_time") not in available_slots(appointment.doctor, new_date):
                messages.error(request, "That new slot is not available.")
                return redirect("appointment_list")
            appointment.appointment_date = new_date
            appointment.appointment_time = new_time
            appointment.status = "Rescheduled"
            appointment.queue_token = (Appointment.objects.filter(doctor=appointment.doctor, appointment_date=new_date, status__in=ACTIVE_STATUSES).exclude(pk=appointment.pk).order_by("-queue_token").values_list("queue_token", flat=True).first() or 0) + 1
            appointment.estimated_wait_minutes = (appointment.queue_token - 1) * appointment.doctor.slot_duration_minutes
            appointment.save(update_fields=("appointment_date", "appointment_time", "status", "queue_token", "estimated_wait_minutes", "updated_at"))
            notify(appointment.patient.user, "appointment_rescheduled", "Appointment rescheduled", f"Appointment #{appointment.appointment_id} was rescheduled to {new_date} at {new_time}.")
        except ValueError:
            messages.error(request, "Enter a valid date and time.")
    elif action == "confirm" and role in ("admin", "doctor"):
        appointment.status = "Confirmed"
        appointment.save(update_fields=("status", "updated_at"))
        notify(appointment.patient.user, "appointment_confirmed", "Appointment confirmed", f"Appointment #{appointment.appointment_id} is confirmed.")
    elif action == "complete" and role in ("admin", "doctor"):
        appointment.status = "Completed"
        appointment.save(update_fields=("status", "updated_at"))
    return redirect("appointment_list")


@role_required("admin", "patient")
def appointment_reschedule(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    if user_role(request.user) == "patient" and appointment.patient.user_id != request.user.id:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    if request.method == "POST":
        return appointment_action(request, appointment_id, "reschedule")
    return render(request, "appointments/appointment_reschedule.html", {
        "appointment": appointment,
        "available_slots": available_slots(appointment.doctor, appointment.appointment_date),
    })