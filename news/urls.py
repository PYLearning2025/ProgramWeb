from django.urls import path
from . import views

urlpatterns = [
    path("", views.news_list, name="NewsList"),
    path("<slug:slug>/", views.news_unit, name="NewsUnit"),
]