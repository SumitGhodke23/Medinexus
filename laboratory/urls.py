from django.urls import path
from . import views

urlpatterns = [path("", views.laboratory_list, name="laboratory_list")]
