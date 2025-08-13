from django.urls import path
from . import views

urlpatterns = [
    path("create/<int:question_id>/", views.review_create, name="CreateReview"),
]