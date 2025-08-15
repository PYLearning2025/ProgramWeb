from django.urls import path
from . import views

urlpatterns = [
    path("", views.review_list, name="ReviewList"),
    path("create/<int:question_id>/", views.review_create, name="CreateReview"),
    path("submit/<int:question_id>/", views.review_submit, name="SubmitReview"),
]