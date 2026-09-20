from django.shortcuts import redirect, render
from patients.models import Patients
from doctors.models import Doctor
from .models import LaboratoryTest
from accounts.permissions import role_required, user_role
from accounts.services import notify
from appointments.models import Appointment


@role_required("admin", "doctor", "patient")
def laboratory_list(request):
	role = user_role(request.user)
	if request.method == "POST" and role in ("admin", "doctor"):
		patient = Patients.objects.filter(pk=request.POST["patient"]).first()
		doctor = Doctor.objects.filter(pk=request.POST["doctor"]).first()
		if role == "doctor" and not Appointment.objects.filter(patient=patient, doctor=doctor, doctor__user=request.user).exists():
			return redirect("laboratory_list")
		LaboratoryTest.objects.create(
			patient_id=request.POST["patient"],
			doctor_id=request.POST["doctor"],
			test_name=request.POST["test_name"],
			test_result=request.POST.get("test_result", ""),
			status=request.POST.get("status", "Requested"),
			technician_notes=request.POST.get("technician_notes", ""),
		)
		if request.POST.get("status") == "Completed":
			notify(patient.user, "lab_report_available", "Lab report available", f"Your {request.POST['test_name']} report is now available in your portal.")
		return redirect("laboratory_list")
	tests = LaboratoryTest.objects.select_related("patient", "doctor").order_by("-test_date", "-test_id")
	if role == "patient":
		tests = tests.filter(patient__user=request.user)
	elif role == "doctor":
		tests = tests.filter(doctor__user=request.user)
	return render(request, "laboratory/laboratory_list.html", {
		"tests": tests,
		"patients": Patients.objects.order_by("full_name") if role == "admin" else Patients.objects.filter(appointment__doctor__user=request.user).distinct(),
		"doctors": Doctor.objects.order_by("full_name") if role == "admin" else Doctor.objects.filter(user=request.user),
		"statuses": LaboratoryTest.TEST_STATUS,
	})

# Create your views here.
