from django.urls import path

from clubadministration.views import *

urlpatterns = [
    path('', ClubInitial.as_view()),
    path('<str:sid>/', ClubDashboard.as_view()),

    path('resetPassword', ClubResetPassword.as_view()),
    path('createUser', ClubCreateUser.as_view()),
    path('deleteUser', ClubDeleteUser.as_view()),
]
