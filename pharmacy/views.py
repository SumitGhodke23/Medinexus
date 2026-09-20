from django.shortcuts import redirect, render
from accounts.permissions import role_required
from .models import Medicine


@role_required("admin")
def overview(request):
	if request.method == "POST":
		Medicine.objects.create(
			medicine_name=request.POST["medicine_name"],
			category=request.POST.get("category", ""),
			quantity=request.POST.get("quantity") or 0,
			reorder_level=request.POST.get("reorder_level") or 10,
			unit_price=request.POST.get("unit_price") or 0,
			expiry_date=request.POST.get("expiry_date") or None,
			supplier=request.POST.get("supplier", ""),
		)
		return redirect("pharmacy_overview")

	return render(request, "pharmacy/overview.html", {
		"medicines": Medicine.objects.filter(active=True),
	})
