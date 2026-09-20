
from django.shortcuts import render
from .models import Patients


def patient_list(request):
    patients = Patients.objects.all().order_by("-id")

    return render(
        request,
        "patients/patient_list.html",
        {
            "patients": patients
        }
    )