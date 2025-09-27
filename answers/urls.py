from django.urls import path
from . import views

urlpatterns = [
    path("create/<int:question_id>/", views.answer_create, name="CreateAnswer"),
    path("submit/", views.answer_submit, name="SubmitAnswer"),
    path("debug/", views.answer_debug, name="DebugAnswer"),
]