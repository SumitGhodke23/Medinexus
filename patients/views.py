
from django.shortcuts import redirect, render
from accounts.permissions import role_required
from .models import Patients


@role_required("admin")
def patient_list(request):
    if request.method == "POST":
        Patients.objects.create(
            full_name=request.POST.get("full_name", "").strip(),
            email=request.POST.get("email") or None,
            phone=request.POST.get("phone") or None,
            date_of_birth=request.POST.get("date_of_birth") or None,
            gender=request.POST.get("gender") or None,
            blood_group=request.POST.get("blood_group") or None,
            address=request.POST.get("address") or None,
            disease=request.POST.get("disease") or None,
        )
        return redirect("patient_list")

    patients = Patients.objects.all().order_by("-patient_id")

    return render(
        request,
        "patients/patient_list.html",
        {
            "patients": patients
        }
    )