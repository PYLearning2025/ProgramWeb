from django.urls import path
from . import views

urlpatterns = [
    path("questionanalysis/", views.analyze_question, name="QuestionAnalysis"),
]