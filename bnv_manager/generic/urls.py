from django.urls import path

from generic.views import Login, Logout, DashboardView

urlpatterns = [
    path("login", Login.as_view()),
    path("logout", Logout.as_view()),
    path("", DashboardView.as_view()),
]
