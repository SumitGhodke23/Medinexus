from django.urls import path
from . import views

urlpatterns = [
    path("", views.doctor_list, name="doctor_list"),
    path("availability/", views.availability, name="doctor_availability"),
]