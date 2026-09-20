from django.shortcuts import redirect, render
from decimal import Decimal, InvalidOperation
from patients.models import Patients
from .models import Bill
from accounts.permissions import role_required, user_role


@role_required("admin", "patient")
def bill_list(request):
	role = user_role(request.user)
	if request.method == "POST" and role == "admin":
		patient_id = request.POST.get("patient")
		if patient_id:
			def amount(name):
				try:
					return Decimal(request.POST.get(name) or "0")
				except InvalidOperation:
					return Decimal("0")

			Bill.objects.create(
				patient_id=patient_id,
				consultation_fee=amount("consultation_fee"),
				medicine_fee=amount("medicine_fee"),
				laboratory_fee=amount("laboratory_fee"),
				room_charges=amount("room_charges"),
				other_charges=amount("other_charges"),
				payment_status=request.POST.get("payment_status") or "Pending",
				notes=request.POST.get("notes", ""),
			)
			return redirect("bill_list")
	bills = Bill.objects.select_related("patient").order_by("-bill_date", "-bill_id")
	if role == "patient":
		bills = bills.filter(patient__user=request.user)
	return render(request, "billing/bill_list.html", {
		"bills": bills,
		"patients": Patients.objects.order_by("full_name") if role == "admin" else Patients.objects.filter(user=request.user),
	})

# Create your views here.
