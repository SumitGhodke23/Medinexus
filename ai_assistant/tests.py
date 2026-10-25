from django.contrib.auth.models import User
from django.test import TestCase

from accounts.models import UserProfile
from ai_assistant.views import answer_question
from billing.models import Bill
from doctors.models import Doctor
from laboratory.models import LaboratoryTest
from patients.models import Patients


class AssistantPrivacyTests(TestCase):
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

	def test_patient_only_gets_own_bill_and_lab_counts(self):
		Bill.objects.create(patient=self.patient)
		Bill.objects.create(patient=self.other_patient)
		LaboratoryTest.objects.create(patient=self.patient, doctor=self.doctor, test_name="Own test")
		LaboratoryTest.objects.create(patient=self.other_patient, doctor=self.doctor, test_name="Other test")

		self.assertEqual(answer_question("How many bills?", self.patient_user), "There are 1 bill in your care scope.")
		self.assertEqual(
			answer_question("How many lab tests?", self.patient_user),
			"There are 1 laboratory test in your care scope.",
		)

	def test_doctor_cannot_get_hospital_wide_bill_count(self):
		Bill.objects.create(patient=self.patient)

		self.assertEqual(
			answer_question("How many bills?", self.doctor.user),
			"Billing summaries are available to patients and administrators.",
		)
