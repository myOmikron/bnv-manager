from django.urls import path

from clubadministration.views import *

urlpatterns = [
    path('', ClubInitial.as_view()),
    path('<str:sid>/', ClubDashboard.as_view()),
]
