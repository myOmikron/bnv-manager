from django.urls import path

from administration.views import *


urlpatterns = [
    path("index", IndexView.as_view()),
    path("domains", DomainView.as_view()),
    path("clubs", ClubOverview.as_view()),
    path("clubs/add", ClubAddView.as_view()),
    path("clubs/delete/<str:name>", ClubDeleteView.as_view()),
    path("clubs/<str:club>", ClubView.as_view()),
    path("clubs/<str:club>/addDomain/<str:domain>", ClubAddDomain.as_view()),
    path("clubs/<str:club>/removeDomain/<str:domain>", ClubRemoveDomain.as_view()),
    path("accounts", AccountOverview.as_view()),
]
