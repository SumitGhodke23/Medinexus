from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render
from appointments.models import Appointment
from beds.models import Bed
from billing.models import Bill
from departments.models import Department
from laboratory.models import LaboratoryTest
from patients.models import Patients
from doctors.models import Doctor


@login_required
def summary(request):
	bills = Bill.objects.all()
	return render(request, "analytics/summary.html", {
		"patients": Patients.objects.count(),
		"doctors": Doctor.objects.count(),
		"appointments": Appointment.objects.count(),
		"available_beds": Bed.objects.filter(status="Available").count(),
		"bills": bills.count(),
		"revenue": sum((bill.total_amount for bill in bills), 0),
		"laboratory_tests": LaboratoryTest.objects.count(),
		"departments": Department.objects.filter(status=True).count(),
		"appointments_by_status": Appointment.objects.values("status").annotate(total=Count("appointment_id")),
	})

# Create your views here.
