from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from patients.models import Patients
from doctors.models import Doctor
from .models import LaboratoryTest


@login_required
def laboratory_list(request):
	if request.method == "POST":
		LaboratoryTest.objects.create(
			patient_id=request.POST["patient"],
			doctor_id=request.POST["doctor"],
			test_name=request.POST["test_name"],
			test_result=request.POST.get("test_result", ""),
			status=request.POST.get("status", "Requested"),
			technician_notes=request.POST.get("technician_notes", ""),
		)
		return redirect("laboratory_list")
	return render(request, "laboratory/laboratory_list.html", {
		"tests": LaboratoryTest.objects.select_related("patient", "doctor").order_by("-test_date", "-test_id"),
		"patients": Patients.objects.order_by("full_name"),
		"doctors": Doctor.objects.order_by("full_name"),
		"statuses": LaboratoryTest.TEST_STATUS,
	})

# Create your views here.
