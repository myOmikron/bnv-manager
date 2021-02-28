from django.urls import path

from administration.views import IndexView, DomainView, GroupView, GroupAddView, GroupDeleteView

urlpatterns = [
    path("index", IndexView.as_view()),
    path("domains", DomainView.as_view()),
    path("groups", GroupView.as_view()),
    path("groups/add", GroupAddView.as_view()),
    path("groups/delete/<str:name>", GroupDeleteView.as_view()),
]
