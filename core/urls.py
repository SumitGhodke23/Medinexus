from django.urls import path
from . import views

urlpatterns = [
    path("", views.public_home, name="public_home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("patient/dashboard/", views.patient_dashboard, name="patient_dashboard"),
    path("doctor/dashboard/", views.doctor_dashboard, name="doctor_dashboard"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
]