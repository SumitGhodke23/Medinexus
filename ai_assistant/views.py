import os
import re
from datetime import datetime

import requests
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from appointments.models import Appointment
from appointments.views import ACTIVE_STATUSES, available_slots
from beds.models import Bed
from billing.models import Bill
from doctors.models import Doctor
from laboratory.models import LaboratoryTest
from patients.models import Patients
from accounts.permissions import role_required, user_role
from accounts.services import notify
from .models import ChatMessage


def ask_ollama(question):
    """Generate an AI answer using the hosted Gemini API."""

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        return "AI service is not configured. Please contact the administrator."

    api_url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-2.5-flash:generateContent"
    )

    prompt = (
        "You are MediNexusAI, a helpful hospital information assistant. "
        "Answer in simple English. Be clear, friendly, and concise. "
        "For general health questions, provide educational information only. "
        "Do not diagnose diseases or replace a qualified doctor. "
        "For emergencies, tell the user to contact local emergency services "
        "or hospital staff immediately. "
        "Never invent patient records, appointments, doctors, test results, "
        "or hospital statistics. "
        "Do not claim to have booked an appointment unless the hospital "
        "booking system confirms it.\n\n"
        f"User question: {question}"
    )

    try:
        response = requests.post(
            api_url,
            params={"key": api_key},
            json={
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.4,
                    "maxOutputTokens": 500,
                },
            },
            timeout=45,
        )

        response.raise_for_status()
        data = response.json()

        candidates = data.get("candidates", [])
        if not candidates:
            return "Sorry, the AI could not generate an answer. Please try again."

        parts = candidates[0].get("content", {}).get("parts", [])
        answer = " ".join(
            part.get("text", "")
            for part in parts
            if part.get("text")
        ).strip()

        return answer or "Sorry, the AI returned an empty answer."

    except requests.Timeout:
        return "The AI is taking too long to respond. Please try again."

    except requests.HTTPError as error:
        status_code = (
            error.response.status_code
            if error.response is not None
            else "unknown"
        )

        if status_code in (401, 403):
            return "The AI API key is invalid or does not have permission."

        if status_code == 429:
            return "The AI service usage limit has been reached. Please try later."

        return f"The AI service returned an error (HTTP {status_code}). Please try again."

    except (requests.RequestException, ValueError):
        return "The AI service is temporarily unavailable. Please try again."


def answer_question(question, user):
    """Answer supported hospital-statistics questions from the database."""
    def phrase(count, singular, plural=None):
        word = singular if count == 1 else (plural or singular + "s")
        return f"{count} {word}"

    text = question.lower()
    role = user_role(user)
    patient = getattr(user, "patient_record", None)
    doctor = getattr(user, "doctor_record", None)

    patients = Patients.objects.all()
    appointments = Appointment.objects.all()
    bills = Bill.objects.all()
    laboratory_tests = LaboratoryTest.objects.all()

    if role == "patient":
        patients = patients.filter(pk=patient.pk) if patient else patients.none()
        appointments = appointments.filter(patient=patient) if patient else appointments.none()
        bills = bills.filter(patient=patient) if patient else bills.none()
        laboratory_tests = (
            laboratory_tests.filter(patient=patient) if patient else laboratory_tests.none()
        )
    elif role == "doctor":
        patients = (
            patients.filter(appointment__doctor=doctor).distinct()
            if doctor else patients.none()
        )
        appointments = appointments.filter(doctor=doctor) if doctor else appointments.none()
        bills = bills.none()
        laboratory_tests = (
            laboratory_tests.filter(doctor=doctor) if doctor else laboratory_tests.none()
        )

    if "patient" in text:
        return f"There are {phrase(patients.count(), 'patient')} in your care scope."

    if "doctor" in text or "care team" in text:
        return f"There are {phrase(Doctor.objects.count(), 'doctor')} in the care team."

    if "appointment" in text or "schedule" in text:
        return f"There are {phrase(appointments.count(), 'appointment')} in your care scope."

    if "bed" in text or "capacity" in text:
        available_beds = Bed.objects.filter(status="Available").count()
        return f"{phrase(available_beds, 'bed')} currently available."

    if "bill" in text or "billing" in text:
        if role == "doctor":
            return "Billing summaries are available to patients and administrators."
        return f"There are {phrase(bills.count(), 'bill')} in your care scope."

    if "lab" in text or "test" in text:
        return f"There are {phrase(laboratory_tests.count(), 'laboratory test')} in your care scope."

    # Let Ollama handle general questions that are not database-statistics questions.
    return None


def _save_exchange(question, answer, patient_id=None):
    ChatMessage.objects.create(
        patient_id=patient_id,
        message_type="User",
        message=question,
    )
    ChatMessage.objects.create(
        patient_id=patient_id,
        message_type="AI",
        message=answer,
    )


def appointment_reply(request, message):
    """Handle the step-by-step appointment booking conversation."""
    pending = request.session.get("voice_appointment")
    text = message.strip()
    lower = text.lower()
    role = user_role(request.user)
    linked_patient = getattr(request.user, "patient_record", None)

    booking_phrases = (
        "book appointment",
        "book an appointment",
        "make appointment",
        "make an appointment",
        "schedule appointment",
        "schedule an appointment",
        "book a doctor",
        "book me",
        "schedule a visit",
    )

    if pending is None and any(phrase in lower for phrase in booking_phrases):
        pending = {"patient": linked_patient.pk} if role == "patient" and linked_patient else {}

        if role == "patient" and not linked_patient:
            return (
                "Your account is not linked to a patient record yet. "
                "Please contact hospital administration."
            ), None

        request.session["voice_appointment"] = pending
        request.session.modified = True

        if pending.get("patient"):
            return "I can book that appointment. Which doctor should I book?", pending.get("patient")
        return "I can book that appointment. What is the patient's full name?", None

    if pending is None:
        return None, None

    if lower in {"cancel", "cancel booking", "stop", "start over"}:
        request.session.pop("voice_appointment", None)
        return "The appointment booking was cancelled. What else can I help with?", None

    if "patient" not in pending:
        name = re.sub(
            r"^(my name is|patient name is|the patient is)\s+",
            "",
            text,
            flags=re.IGNORECASE,
        ).strip()

        if len(name.split()) < 2:
            return "Please tell me the patient's full name, for example, Mahesh Patil.", None

        patient_record = Patients.objects.filter(full_name__iexact=name).first()
        if patient_record is None:
            patient_record = Patients.objects.create(full_name=name)

        pending["patient"] = patient_record.patient_id
        request.session["voice_appointment"] = pending
        request.session.modified = True

        available_doctors = list(
            Doctor.objects.filter(available=True).values_list("full_name", flat=True)
        )
        doctor_names = ", ".join(available_doctors) or "none currently"
        return (
            "Thanks. Which doctor should I book with? Available doctors are: "
            f"{doctor_names}.",
            patient_record.patient_id,
        )

    if "doctor" not in pending:
        clean_name = re.sub(
            r"^(doctor|dr\.?)[:\s]+",
            "",
            text,
            flags=re.IGNORECASE,
        ).strip()
        doctor_record = Doctor.objects.filter(
            full_name__icontains=clean_name,
            available=True,
        ).first()

        if doctor_record is None:
            return "I could not find that available doctor. Please say the doctor's full name.", pending.get("patient")

        pending["doctor"] = doctor_record.doctor_id
        request.session["voice_appointment"] = pending
        request.session.modified = True
        return "What date should I use? Please say it like 20 September 2026.", pending.get("patient")

    if "date" not in pending:
        date_match = re.search(
            r"(\d{1,2}[\s/-]+[A-Za-z]+[\s/-]+\d{4}|\d{4}-\d{1,2}-\d{1,2}|\d{1,2}/\d{1,2}/\d{4})",
            text,
        )
        parsed_date = None

        if date_match:
            date_text = date_match.group(1).strip()
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

        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)
        meridiem = time_match.group(3)

        if meridiem == "pm" and hour < 12:
            hour += 12
        if meridiem == "am" and hour == 12:
            hour = 0
        if hour > 23 or minute > 59:
            return "That time is not valid. Please try again, for example 10:30 AM.", pending.get("patient")

        pending["time"] = f"{hour:02d}:{minute:02d}"
        request.session["voice_appointment"] = pending
        request.session.modified = True
        return "What is the reason for the visit?", pending.get("patient")

    pending["reason"] = text
    doctor_record = Doctor.objects.get(pk=pending["doctor"])

    from datetime import date, time

    appointment_date = date.fromisoformat(pending["date"])
    appointment_time = time.fromisoformat(pending["time"])

    if pending["time"] not in available_slots(doctor_record, appointment_date):
        return "That slot is no longer available. Please choose another time.", pending["patient"]

    last_token = (
        Appointment.objects.filter(
            doctor=doctor_record,
            appointment_date=appointment_date,
            status__in=ACTIVE_STATUSES,
        )
        .order_by("-queue_token")
        .values_list("queue_token", flat=True)
        .first()
        or 0
    )

    appointment = Appointment.objects.create(
        patient_id=pending["patient"],
        doctor=doctor_record,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        reason=pending["reason"],
        queue_token=last_token + 1,
        estimated_wait_minutes=last_token * doctor_record.slot_duration_minutes,
    )

    # Send a notification only when the patient record has a linked user account.
    patient_user = getattr(appointment.patient, "user", None)
    if patient_user:
        notify(
            patient_user,
            "appointment_booked",
            "Appointment booked",
            (
                f"Appointment #{appointment.appointment_id} with Dr. "
                f"{appointment.doctor.full_name} is booked. "
                f"Token {appointment.queue_token}."
            ),
        )

    request.session.pop("voice_appointment", None)
    return (
        f"Appointment booked for {appointment.patient.full_name} with Dr. "
        f"{appointment.doctor.full_name} on {appointment.appointment_date} "
        f"at {appointment.appointment_time}.",
        appointment.patient_id,
    )


def process_message(request, message):
    """Route booking messages, database questions, and general AI questions."""
    answer, patient_id = appointment_reply(request, message)

    if answer is None:
        answer = answer_question(message, request.user)

        if answer is None:
            answer = ask_ollama(message)

    patient = getattr(request.user, "patient_record", None)
    if patient_id is None and user_role(request.user) == "patient" and patient:
        patient_id = patient.pk

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
        conversation = conversation.filter(
            patient__appointment__doctor__user=request.user
        ).distinct()

    if request.method == "POST":
        message = request.POST.get("message", "").strip()
        if message:
            process_message(request, message)
        return redirect("ai_chat")

    if role == "admin":
        visible_patients = Patients.objects.order_by("full_name")
    elif role == "doctor":
        visible_patients = Patients.objects.filter(
            appointment__doctor__user=request.user
        ).distinct()
    else:
        visible_patients = (
            Patients.objects.filter(pk=patient.pk) if patient else Patients.objects.none()
        )

    return render(
        request,
        "ai_assistant/chat.html",
        {
            "patients": visible_patients,
            "messages": conversation,
        },
    )


@role_required("admin", "doctor", "patient")
@require_POST
def voice_api(request):
    question = request.POST.get("question", "").strip()
    if not question:
        return JsonResponse({"error": "Please ask a question."}, status=400)

    answer = process_message(request, question)
    return JsonResponse({"question": question, "answer": answer})
