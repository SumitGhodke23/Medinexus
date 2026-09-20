from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from patients.models import Patients
from .models import Bed


@login_required
def bed_list(request):
	if request.method == "POST":
		Bed.objects.create(
			bed_number=request.POST["bed_number"],
			room_number=request.POST["room_number"],
			ward_name=request.POST["ward_name"],
			bed_type=request.POST.get("bed_type", "General"),
			status=request.POST.get("status", "Available"),
			patient_id=request.POST.get("patient") or None,
			notes=request.POST.get("notes", ""),
		)
		return redirect("bed_list")
	return render(request, "beds/bed_list.html", {
		"beds": Bed.objects.select_related("patient").order_by("ward_name", "bed_number"),
		"patients": Patients.objects.order_by("full_name"),
		"bed_types": Bed.BED_TYPES,
		"statuses": Bed.BED_STATUS,
	})

# Create your views here.
