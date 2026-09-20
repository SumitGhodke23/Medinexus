from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("patients/", include("patients.urls")),
]
from django.urls import path
from . import views

urlpatterns = [
    path("", views.patient_list, name="patient_list"),
]