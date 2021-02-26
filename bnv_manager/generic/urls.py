from django.urls import path

from generic.views import Login, Logout

urlpatterns = [
    path("login", Login.as_view()),
    path("logout", Logout.as_view()),
]
