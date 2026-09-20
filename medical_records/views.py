from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from patients.models import Patients
from doctors.models import Doctor
from .models import MedicalRecord
from accounts.permissions import role_required, user_role
from appointments.models import Appointment


@role_required("admin", "patient", "doctor")
def medical_record_list(request):
    records = MedicalRecord.objects.select_related(
        "patient",
        "doctor"
    ).order_by("-record_id")
    if user_role(request.user) == "patient":
        records = records.filter(patient__user=request.user)
    elif user_role(request.user) == "doctor":
        records = records.filter(doctor__user=request.user)

    return render(
        request,
        "medical_records/medical_record_list.html",
        {"records": records}
    )


@role_required("admin", "doctor")
def medical_record_add(request):
    if request.method == "POST":
        patient_id = request.POST.get("patient")
        doctor_id = request.POST.get("doctor")
        disease = request.POST.get("disease")

        if not all((patient_id, disease)):
            messages.error(request, "Patient and disease are required.")
        else:
            doctor = getattr(request.user, "doctor_record", None)
            if user_role(request.user) == "doctor" and not Appointment.objects.filter(patient_id=patient_id, doctor=doctor).exists():
                messages.error(request, "You can only add records for patients assigned to you.")
                return redirect("medical_record_add")
            MedicalRecord.objects.create(
                patient_id=patient_id,
                doctor=doctor if user_role(request.user) == "doctor" else (Doctor.objects.filter(pk=doctor_id).first() if doctor_id else None),
                disease=disease,
                symptoms=request.POST.get("symptoms", ""),
                diagnosis=request.POST.get("diagnosis", ""),
                treatment=request.POST.get("treatment", ""),
                prescription=request.POST.get("prescription", ""),
            )
            messages.success(request, "Medical record created successfully.")
            return redirect("medical_record_list")

    return render(
        request,
        "medical_records/medical_record_add.html",
        {
            "patients": Patients.objects.order_by("full_name") if user_role(request.user) == "admin" else Patients.objects.filter(appointment__doctor__user=request.user).distinct().order_by("full_name"),
            "doctors": Doctor.objects.order_by("full_name"),
        },
    )