from django.urls import path
from . import views

urlpatterns = [
    path("", views.game, name="Game"),
    path("wrong/", views.wrong, name="Wrong"),
    path("draw/", views.draw, name="Draw"),
    path("result/<int:card_id>/", views.result, name="Result"),
    path("check_answer/", views.check_answer, name="Check_Answer"),
    path("draw_card/", views.draw_card, name="Draw_Card"),
]