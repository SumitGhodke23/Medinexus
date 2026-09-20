from django.urls import path
from . import views

urlpatterns = [
	path("", views.chat, name="ai_chat"),
	path("voice/", views.voice_api, name="voice_api"),
]
