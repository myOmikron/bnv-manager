from django.urls import path

from administration.views import *


urlpatterns = [
    path("index", IndexView.as_view()),
    path("domains", DomainView.as_view()),
    path("groups", ClubView.as_view()),
    path("groups/add", ClubAddView.as_view()),
    path("groups/delete/<str:name>", ClubDeleteView.as_view()),
]
