from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.question_create, name="CreateQuestion"),
    path("<int:question_id>/", views.question_detail, name="QuestionDetail"),
    path("<int:question_id>/<int:version>/", views.question_version, name="QuestionDetailVersion"),
    path("<int:question_id>/update/", views.question_update, name="QuestionUpdate"),
    path("list/", views.question_list, name="QuestionList"),
]