from django.shortcuts import render
from accounts.permissions import role_required
from beds.models import Bed
from departments.models import Department


@role_required("admin")
def overview(request):
	return render(request, "hospital/overview.html", {
		"beds": Bed.objects.count(),
		"available_beds": Bed.objects.filter(status="Available").count(),
		"departments": Department.objects.filter(status=True),
	})

# Create your views here.
