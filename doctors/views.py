from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .models import Doctor


@login_required
def doctor_list(request):
    if request.method == "POST":
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

    doctors = Doctor.objects.all()

    return render(
        request,
        "doctors/doctor_list.html",
        {
            "doctors": doctors
        }
    )