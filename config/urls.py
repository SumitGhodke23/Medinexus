from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("core.urls")),
    path("patients/", include("patients.urls")),
    path("doctors/", include("doctors.urls")),
    path(
    "appointments/",
    include("appointments.urls")
),

path(
    "medical-records/",
    include("medical_records.urls")
),
path("billing/", include("billing.urls")),
path("beds/", include("beds.urls")),
path("laboratory/", include("laboratory.urls")),
path("departments/", include("departments.urls")),
path("prescriptions/", include("prescriptions.urls")),
path("analytics/", include("analytics.urls")),
path("ai-assistant/", include("ai_assistant.urls")),
path("hospital/", include("hospital.urls")),
path("pharmacy/", include("pharmacy.urls")),
]