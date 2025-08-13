from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.report_create, name="CreateReport"),
]