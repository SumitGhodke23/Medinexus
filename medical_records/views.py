from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from patients.models import Patients
from doctors.models import Doctor
from .models import MedicalRecord


@login_required
def medical_record_list(request):
    records = MedicalRecord.objects.select_related(
        "patient",
        "doctor"
    ).order_by("-record_id")

    return render(
        request,
        "medical_records/medical_record_list.html",
        {"records": records}
    )


@login_required
def medical_record_add(request):
    if request.method == "POST":
        patient_id = request.POST.get("patient")
        doctor_id = request.POST.get("doctor")
        disease = request.POST.get("disease")

        if not all((patient_id, disease)):
            messages.error(request, "Patient and disease are required.")
        else:
            MedicalRecord.objects.create(
                patient_id=patient_id,
                doctor_id=doctor_id or None,
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
            "patients": Patients.objects.order_by("full_name"),
            "doctors": Doctor.objects.order_by("full_name"),
        },
    )