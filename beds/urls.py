from django.urls import path
from . import views

urlpatterns = [path("", views.bed_list, name="bed_list")]
