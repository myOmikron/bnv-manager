from django.urls import path

from administration.views import *


urlpatterns = [
    path("index", IndexView.as_view()),
    path("domains", DomainView.as_view()),
    path("clubs", ClubView.as_view()),
    path("clubs/add", ClubAddView.as_view()),
    path("clubs/delete/<str:name>", ClubDeleteView.as_view()),
]
