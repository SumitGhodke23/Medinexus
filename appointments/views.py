from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from patients.models import Patients
from doctors.models import Doctor
from .models import Appointment


@login_required
def appointment_list(request):
    appointments = Appointment.objects.select_related(
        "patient",
        "doctor"
    ).order_by("-appointment_date", "-appointment_time")

    return render(
        request,
        "appointments/appointment_list.html",
        {"appointments": appointments}
    )


@login_required
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
            Appointment.objects.create(
                patient_id=patient_id,
                doctor_id=doctor_id,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                reason=reason
            )
            messages.success(request, "Appointment created successfully.")
            return redirect("appointment_list")

    return render(
        request,
        "appointments/appointment_add.html",
        {
            "patients": Patients.objects.order_by("full_name"),
            "doctors": Doctor.objects.filter(available=True).order_by("full_name"),
        },
    )