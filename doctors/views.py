from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .models import Doctor
from accounts.permissions import role_required


def doctor_list(request):
    if request.method == "POST" and request.user.is_staff:
        Doctor.objects.create(
            full_name=request.POST["full_name"],
            specialization=request.POST["specialization"],
            education=request.POST["education"],
            experience=request.POST.get("experience") or 0,
            email=request.POST.get("email", ""),
            phone=request.POST.get("phone", ""),
            available=request.POST.get("available") == "on",
        )
        return redirect("doctor_list")

    doctors = Doctor.objects.select_related("department").all()

    return render(
        request,
        "doctors/doctor_list.html",
        {
            "doctors": doctors
        }
    )


@role_required("doctor")
def availability(request):
    doctor = getattr(request.user, "doctor_record", None)
    if request.method == "POST" and doctor:
        doctor.available = request.POST.get("available") == "on"
        doctor.availability_start = request.POST.get("availability_start") or doctor.availability_start
        doctor.availability_end = request.POST.get("availability_end") or doctor.availability_end
        doctor.slot_duration_minutes = max(5, int(request.POST.get("slot_duration_minutes") or doctor.slot_duration_minutes))
        doctor.save(update_fields=("available", "availability_start", "availability_end", "slot_duration_minutes"))
        return redirect("doctor_availability")
    return render(request, "doctors/availability.html", {"doctor": doctor})