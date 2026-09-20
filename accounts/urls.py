from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    path(
        "login/",
        views.login_view,
        name="login",
    ),
    path("patient-login/", views.role_login, {"role": "patient"}, name="patient_login"),
    path("patient-signup/", views.patient_signup, name="patient_signup"),
    path("doctor-login/", views.role_login, {"role": "doctor"}, name="doctor_login"),
    path("admin-login/", views.role_login, {"role": "admin"}, name="admin_login"),
    path("notifications/", views.notification_center, name="notification_center"),
    path("language/", views.set_language, name="set_language"),
    path("profile/", views.profile, name="profile"),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
]