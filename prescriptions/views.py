from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from patients.models import Patients
from doctors.models import Doctor
from medical_records.models import MedicalRecord
from .models import Prescription
from accounts.permissions import role_required, user_role
from accounts.services import notify
from appointments.models import Appointment


@role_required("admin", "patient", "doctor")
def prescription_list(request):
    role = user_role(request.user)
    prescriptions = Prescription.objects.select_related("patient", "doctor").order_by("-prescribed_date")
    if role == "patient":
        prescriptions = prescriptions.filter(patient__user=request.user)
    elif role == "doctor":
        prescriptions = prescriptions.filter(doctor__user=request.user)
    if request.method == "POST" and role in ("admin", "doctor"):
        doctor = getattr(request.user, "doctor_record", None)
        patient = Patients.objects.filter(pk=request.POST["patient"]).first()
        if role == "doctor" and not Appointment.objects.filter(patient=patient, doctor=doctor).exists():
            return redirect("prescription_list")
        Prescription.objects.create(
            patient_id=request.POST["patient"],
            doctor=doctor if role == "doctor" else (Doctor.objects.filter(pk=request.POST.get("doctor")).first() if request.POST.get("doctor") else None),
            medical_record_id=request.POST.get("medical_record") or None,
            medicine_name=request.POST["medicine_name"],
            dosage=request.POST["dosage"],
            frequency=request.POST["frequency"],
            duration=request.POST["duration"],
            instructions=request.POST.get("instructions", ""),
        )
        notify(patient.user, "prescription_added", "Prescription added", f"A new prescription for {patient.full_name} is available in your portal.")
        return redirect("prescription_list")
    return render(request, "prescriptions/prescription_list.html", {
        "prescriptions": prescriptions,
        "patients": Patients.objects.order_by("full_name") if role == "admin" else Patients.objects.filter(appointment__doctor__user=request.user).distinct().order_by("full_name"),
        "doctors": Doctor.objects.order_by("full_name"),
        "records": MedicalRecord.objects.select_related("patient").order_by("-record_date"),
    })