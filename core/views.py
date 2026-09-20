from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from patients.models import Patients
from doctors.models import Doctor
from appointments.models import Appointment
from beds.models import Bed
from billing.models import Bill
from laboratory.models import LaboratoryTest

@login_required
def dashboard(request):
    context = {
        "total_patients": Patients.objects.count(),
        "total_doctors": Doctor.objects.count(),
        "total_appointments": Appointment.objects.count(),
        "available_beds": Bed.objects.filter(
            status="Available"
        ).count(),
        "total_bills": Bill.objects.count(),
        "total_lab_tests": LaboratoryTest.objects.count(),
        "recent_appointments": Appointment.objects.order_by(
            "-appointment_date"
        )[:5],
    }

    return render(
        request,
        "core/dashboard.html",
        context
    )
   


def patient_list(request):
    patients = Patients.objects.all()

    context = {
        "patients": patients
    }

    return render(
        request,
        "patients/patient_list.html",
        context
    )