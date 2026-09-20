from django.urls import path
from . import views

urlpatterns = [path("", views.overview, name="pharmacy_overview")]
