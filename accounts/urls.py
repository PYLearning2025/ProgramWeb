from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="Index"),
    path("login/", views.login, name="Login"),
    path("logout/", views.logout, name="Logout"),
    path("register/", views.register, name="Register"),
]