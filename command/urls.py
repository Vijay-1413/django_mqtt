from django.urls import path
from .views import SendCommandAPIView

urlpatterns = [
    path("", SendCommandAPIView.as_view()),
]