from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from datetime import datetime
import re
from appointments.models import Appointment
from appointments.views import ACTIVE_STATUSES, available_slots
from beds.models import Bed
from billing.models import Bill
from doctors.models import Doctor
from laboratory.models import LaboratoryTest
from patients.models import Patients
from .models import ChatMessage
from accounts.permissions import role_required, user_role
from accounts.services import notify


def answer_question(question):
	def phrase(count, singular, plural=None):
		return f"{count} {singular if count == 1 else (plural or singular + 's')}"

	text = question.lower()
	if "patient" in text:
		return f"There are {phrase(Patients.objects.count(), 'patient')} registered in medinexusai."
	if "doctor" in text or "care team" in text:
		return f"There are {phrase(Doctor.objects.count(), 'doctor')} in the care team."
	if "appointment" in text or "schedule" in text:
		return f"There are {phrase(Appointment.objects.count(), 'appointment')} in the system."
	if "bed" in text or "capacity" in text:
		return f"{phrase(Bed.objects.filter(status='Available').count(), 'bed')} currently available."
	if "bill" in text or "billing" in text:
		return f"There are {phrase(Bill.objects.count(), 'bill')} recorded."
	if "lab" in text or "test" in text:
		return f"There are {phrase(LaboratoryTest.objects.count(), 'laboratory test')} recorded."
	return "I can answer questions about patients, doctors, appointments, available beds, bills, and lab tests."


def _save_exchange(question, answer, patient_id=None):
	ChatMessage.objects.create(patient_id=patient_id, message_type="User", message=question)
	ChatMessage.objects.create(patient_id=patient_id, message_type="AI", message=answer)


def appointment_reply(request, message):
	pending = request.session.get("voice_appointment")
	text = message.strip()
	lower = text.lower()
	role = user_role(request.user)
	linked_patient = getattr(request.user, "patient_record", None)

	if pending is None and any(word in lower for word in ("book appointment", "book an appointment", "make appointment", "make an appointment", "schedule appointment", "schedule an appointment", "book a doctor", "book me", "schedule a visit")):
		pending = {"patient": linked_patient.pk} if role == "patient" and linked_patient else {}
		if role == "patient" and not linked_patient:
			return "Your account is not linked to a patient record yet. Contact hospital administration.", None
		request.session["voice_appointment"] = pending
		request.session.modified = True
		return ("I can book that appointment. Which doctor should I book?" if pending.get("patient") else "I can book that appointment. What is the patient's full name?"), pending.get("patient")

	if pending is None:
		return None, None

	if lower in {"cancel", "cancel booking", "stop", "start over"}:
		request.session.pop("voice_appointment", None)
		return "The appointment booking was cancelled. What else can I help with?", None

	if "patient" not in pending:
		name = re.sub(r"^(my name is|patient name is|the patient is)\s+", "", text, flags=re.I).strip()
		if len(name.split()) < 2:
			return "Please tell me the patient's full name, for example, Mahesh Patil.", None
		patient = Patients.objects.filter(full_name__iexact=name).first()
		if patient is None:
			patient = Patients.objects.create(full_name=name)
		pending["patient"] = patient.patient_id
		request.session["voice_appointment"] = pending
		request.session.modified = True
		return f"Thanks. Should I book with which doctor? Available doctors are: {', '.join(Doctor.objects.filter(available=True).values_list('full_name', flat=True)) or 'none currently'}.", patient.patient_id

	if "doctor" not in pending:
		clean_name = re.sub(r"^(doctor|dr\.?)[\s:]+", "", text, flags=re.I).strip()
		doctor = Doctor.objects.filter(full_name__icontains=clean_name, available=True).first()
		if doctor is None:
			return "I could not find that available doctor. Please say the doctor's full name.", pending.get("patient")
		pending["doctor"] = doctor.doctor_id
		request.session["voice_appointment"] = pending
		request.session.modified = True
		return "What date should I use? Please say it like 20 September 2026.", pending.get("patient")

	if "date" not in pending:
		date_match = re.search(r"(\d{1,2}[\s/-]+[A-Za-z]+[\s/-]+\d{4}|\d{4}-\d{1,2}-\d{1,2})", text)
		parsed_date = None
		for date_text in ([date_match.group(1)] if date_match else []):
			for date_format in ("%d %B %Y", "%d %b %Y", "%Y-%m-%d", "%d/%m/%Y"):
				try:
					parsed_date = datetime.strptime(date_text, date_format).date()
					break
				except ValueError:
					continue
		if parsed_date is None:
			return "I need the date with the year, for example 20 September 2026.", pending.get("patient")
		pending["date"] = parsed_date.isoformat()
		request.session["voice_appointment"] = pending
		request.session.modified = True
		return "What time should I book? For example, 10:30 AM.", pending.get("patient")

	if "time" not in pending:
		time_match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", lower)
		if not time_match:
			return "I need a time, for example 10:30 AM.", pending.get("patient")
		hour = int(time_match.group(1)); minute = int(time_match.group(2) or 0); meridiem = time_match.group(3)
		if meridiem == "pm" and hour < 12: hour += 12
		if meridiem == "am" and hour == 12: hour = 0
		if hour > 23 or minute > 59: return "That time is not valid. Please try again, for example 10:30 AM.", pending.get("patient")
		pending["time"] = f"{hour:02d}:{minute:02d}"
		request.session["voice_appointment"] = pending
		request.session.modified = True
		return "What is the reason for the visit?", pending.get("patient")

	pending["reason"] = text
	doctor = Doctor.objects.get(pk=pending["doctor"])
	from datetime import date, time
	appointment_date = date.fromisoformat(pending["date"])
	appointment_time = time.fromisoformat(pending["time"])
	if pending["time"] not in available_slots(doctor, appointment_date):
		return "That slot is no longer available. Please choose another time.", pending["patient"]
	last_token = Appointment.objects.filter(doctor=doctor, appointment_date=appointment_date, status__in=ACTIVE_STATUSES).order_by("-queue_token").values_list("queue_token", flat=True).first() or 0
	appointment = Appointment.objects.create(patient_id=pending["patient"], doctor=doctor, appointment_date=appointment_date, appointment_time=appointment_time, reason=pending["reason"], queue_token=last_token + 1, estimated_wait_minutes=last_token * doctor.slot_duration_minutes)
	notify(appointment.patient.user, "appointment_booked", "Appointment booked", f"Appointment #{appointment.appointment_id} with Dr. {appointment.doctor.full_name} is booked. Token {appointment.queue_token}.")
	request.session.pop("voice_appointment", None)
	return f"Appointment booked for {appointment.patient.full_name} with Dr. {appointment.doctor.full_name} on {appointment.appointment_date} at {appointment.appointment_time}.", appointment.patient_id


def process_message(request, message):
	answer, patient_id = appointment_reply(request, message)
	if answer is None:
		answer = answer_question(message)
	_save_exchange(message, answer, patient_id)
	return answer


@role_required("admin", "doctor", "patient")
def chat(request):
	role = user_role(request.user)
	patient = getattr(request.user, "patient_record", None)
	conversation = ChatMessage.objects.select_related("patient").order_by("created_at")
	if role == "patient":
		conversation = conversation.filter(patient=patient) if patient else conversation.none()
	elif role == "doctor":
		conversation = conversation.filter(patient__appointment__doctor__user=request.user).distinct()
	if request.method == "POST":
		message = request.POST.get("message", "").strip()
		if message:
			patient_id = patient.pk if role == "patient" and patient else request.POST.get("patient") or None
			answer = process_message(request, message)
		return redirect("ai_chat")
	return render(request, "ai_assistant/chat.html", {
		"patients": Patients.objects.order_by("full_name") if role == "admin" else Patients.objects.filter(appointment__doctor__user=request.user).distinct() if role == "doctor" else Patients.objects.filter(pk=patient.pk) if patient else Patients.objects.none(),
		"messages": conversation,
	})


@role_required("admin", "doctor", "patient")
@require_POST
def voice_api(request):
	question = request.POST.get("question", "").strip()
	if not question:
		return JsonResponse({"error": "Please ask a question."}, status=400)

	answer = process_message(request, question)
	return JsonResponse({"question": question, "answer": answer})

# Create your views here.
