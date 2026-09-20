from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from patients.models import Patients

from .forms import PatientSignupForm
from .models import UserProfile
from .permissions import user_role


def login_view(request):
	return render(request, "accounts/login_options.html")


def patient_signup(request):
	form = PatientSignupForm(request.POST or None)
	if request.method == "POST" and form.is_valid():
		with transaction.atomic():
			user = form.save()
			UserProfile.objects.create(user=user, role="patient")
		return redirect("patient_login")
	return render(request, "accounts/patient_signup.html", {"form": form})


def role_login(request, role):
	form = AuthenticationForm(request, data=request.POST or None)
	if request.method == "POST" and form.is_valid():
		user = form.get_user()
		if user_role(user) != role:
			form.add_error(None, "This account does not have access to the selected login.")
		else:
			login(request, user)
			if role == "admin":
				return redirect("admin_dashboard")
			if role == "doctor":
				return redirect("doctor_dashboard")
			return redirect("patient_dashboard")

	return render(request, "accounts/role_login.html", {
		"form": form,
		"role": role,
		"role_title": {"patient": "Patient", "doctor": "Doctor", "admin": "Admin"}[role],
	})


@login_required
def notification_center(request):
	if request.method == "POST":
		request.user.notifications.filter(read_at__isnull=True).update(read_at=timezone.now())
		return redirect("notification_center")
	return render(request, "accounts/notification_center.html", {
		"notifications": request.user.notifications.all(),
	})


@login_required
def set_language(request):
	if request.method == "POST" and request.POST.get("language") in ("en", "hi", "mr"):
		request.session["language"] = request.POST["language"]
	return redirect(request.POST.get("next") or "dashboard")


@login_required
def profile(request):
	patient = getattr(request.user, "patient_record", None)
	if request.method == "POST" and patient:
		patient.email = request.POST.get("email") or patient.email
		patient.phone = request.POST.get("phone") or patient.phone
		patient.address = request.POST.get("address") or patient.address
		patient.save(update_fields=("email", "phone", "address"))
		return redirect("profile")
	return render(request, "accounts/profile.html", {"patient": patient})
