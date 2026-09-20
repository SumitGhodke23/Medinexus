

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
]