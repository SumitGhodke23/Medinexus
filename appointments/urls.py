

from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.appointment_list,
        name="appointment_list"
    ),
    path(
        "add/",
        views.appointment_add,
        name="appointment_add"
    ),
    path("<int:appointment_id>/reschedule/", views.appointment_reschedule, name="appointment_reschedule"),
    path("<int:appointment_id>/<str:action>/", views.appointment_action, name="appointment_action"),
]