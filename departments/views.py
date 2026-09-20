from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .models import Department


@login_required
def department_list(request):
	if request.method == "POST":
		Department.objects.create(
			department_name=request.POST["department_name"],
			department_code=request.POST["department_code"],
			head_of_department=request.POST.get("head_of_department", ""),
			description=request.POST.get("description", ""),
			contact_number=request.POST.get("contact_number", ""),
		)
		return redirect("department_list")
	return render(request, "departments/department_list.html", {
		"departments": Department.objects.order_by("department_name"),
	})

# Create your views here.
