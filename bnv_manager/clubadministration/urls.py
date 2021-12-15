from django.urls import path

from clubadministration.views import *

urlpatterns = [
    path('', ClubDashboard.as_view()),
]
