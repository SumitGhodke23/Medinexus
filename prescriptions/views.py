from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from patients.models import Patients
from doctors.models import Doctor
from medical_records.models import MedicalRecord
from .models import Prescription


@login_required
def prescription_list(request):
    if request.method == "POST":
        Prescription.objects.create(
            patient_id=request.POST["patient"],
            doctor_id=request.POST.get("doctor") or None,
            medical_record_id=request.POST.get("medical_record") or None,
            medicine_name=request.POST["medicine_name"],
            dosage=request.POST["dosage"],
            frequency=request.POST["frequency"],
            duration=request.POST["duration"],
            instructions=request.POST.get("instructions", ""),
        )
        return redirect("prescription_list")
    return render(request, "prescriptions/prescription_list.html", {
        "prescriptions": Prescription.objects.select_related("patient", "doctor").order_by("-prescribed_date"),
        "patients": Patients.objects.order_by("full_name"),
        "doctors": Doctor.objects.order_by("full_name"),
        "records": MedicalRecord.objects.select_related("patient").order_by("-record_date"),
    })