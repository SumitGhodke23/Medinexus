from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserProfile
from billing.models import Bill
from doctors.models import Doctor
from laboratory.models import LaboratoryTest
from patients.models import Patients


class DashboardPrivacyTests(TestCase):
	def setUp(self):
		self.patient_user = User.objects.create_user(username="patient", password="test-pass-123")
		UserProfile.objects.create(user=self.patient_user, role="patient")
		self.patient = Patients.objects.create(user=self.patient_user, full_name="Test Patient")

		other_user = User.objects.create_user(username="other", password="test-pass-123")
		UserProfile.objects.create(user=other_user, role="patient")
		self.other_patient = Patients.objects.create(user=other_user, full_name="Other Patient")

		doctor_user = User.objects.create_user(username="doctor", password="test-pass-123")
		UserProfile.objects.create(user=doctor_user, role="doctor")
		self.doctor = Doctor.objects.create(
			user=doctor_user,
			full_name="Test Doctor",
			specialization="General",
			education="MD",
			experience=5,
		)

	def test_patient_dashboard_limits_bill_and_lab_counts_to_patient(self):
		Bill.objects.create(patient=self.patient)
		Bill.objects.create(patient=self.other_patient)
		LaboratoryTest.objects.create(
			patient=self.patient,
			doctor=self.doctor,
			test_name="Patient test",
		)
		LaboratoryTest.objects.create(
			patient=self.other_patient,
			doctor=self.doctor,
			test_name="Other patient test",
		)
		self.client.force_login(self.patient_user)

		response = self.client.get(reverse("patient_dashboard"))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context["total_bills"], 1)
		self.assertEqual(response.context["total_lab_tests"], 1)
		self.assertEqual(response.context["private_bills"], 1)
		self.assertEqual(response.context["private_lab_tests"], 1)
