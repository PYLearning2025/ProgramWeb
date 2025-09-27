from django.urls import path
from . import views

urlpatterns = [
    path("", views.userinfo, name="UserInfo"),
    path("updateimg/", views.update_profile_img, name="UpdateProfileImg"),
    path("questions/", views.user_dashboard, name="UserinfoQuestions"),
]