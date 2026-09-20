from django.shortcuts import redirect, render
from patients.models import Patients
from doctors.models import Doctor
from appointments.models import Appointment
from beds.models import Bed
from billing.models import Bill
from laboratory.models import LaboratoryTest
from medical_records.models import MedicalRecord
from prescriptions.models import Prescription
from accounts.models import Notification
from accounts.permissions import role_required, user_role
from departments.models import Department


def public_home(request):
    return render(request, "core/public_home.html", {
        "departments": Department.objects.filter(status=True).order_by("department_name"),
        "doctors": Doctor.objects.filter(available=True).select_related("department").order_by("full_name"),
    })

def _dashboard_context(request):
    role = user_role(request.user)
    patient = getattr(request.user, "patient_record", None)
    doctor = getattr(request.user, "doctor_record", None)
    appointments = Appointment.objects.all()
    if role == "patient":
        appointments = appointments.filter(patient=patient) if patient else appointments.none()
    elif role == "doctor":
        appointments = appointments.filter(doctor=doctor) if doctor else appointments.none()
    context = {
        "role": role,
        "total_patients": Patients.objects.filter(user=request.user).count() if role == "patient" else Patients.objects.count(),
        "total_doctors": Doctor.objects.filter(user=request.user).count() if role == "doctor" else Doctor.objects.count(),
        "total_appointments": appointments.count(),
        "available_beds": Bed.objects.filter(
            status="Available"
        ).count(),
        "total_bills": Bill.objects.count(),
        "total_lab_tests": LaboratoryTest.objects.count(),
        "recent_appointments": appointments.select_related("patient", "doctor").order_by("-appointment_date")[:5],
        "private_records": MedicalRecord.objects.filter(patient=patient).count() if role == "patient" and patient else MedicalRecord.objects.filter(doctor=doctor).count() if role == "doctor" and doctor else MedicalRecord.objects.count(),
        "private_prescriptions": Prescription.objects.filter(patient=patient).count() if role == "patient" and patient else Prescription.objects.filter(doctor=doctor).count() if role == "doctor" and doctor else Prescription.objects.count(),
        "private_lab_tests": LaboratoryTest.objects.filter(patient=patient).count() if role == "patient" and patient else LaboratoryTest.objects.filter(doctor=doctor).count() if role == "doctor" and doctor else LaboratoryTest.objects.count(),
        "private_bills": Bill.objects.filter(patient=patient).count() if role == "patient" and patient else Bill.objects.count(),
        "unread_notifications": Notification.objects.filter(user=request.user, read_at__isnull=True).count(),
    }

    return context


@role_required("patient")
def patient_dashboard(request):
    return render(request, "core/patient_dashboard.html", _dashboard_context(request))


@role_required("doctor")
def doctor_dashboard(request):
    return render(request, "core/doctor_dashboard.html", _dashboard_context(request))


@role_required("admin")
def admin_dashboard(request):
    return render(request, "core/admin_dashboard.html", _dashboard_context(request))


@role_required("patient", "doctor", "admin")
def dashboard(request):
    role = user_role(request.user)
    return redirect({
        "patient": "patient_dashboard",
        "doctor": "doctor_dashboard",
        "admin": "admin_dashboard",
    }[role])
   


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