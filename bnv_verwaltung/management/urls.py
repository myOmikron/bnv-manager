from django.urls import path

from management.views import IndexView, AddView

urlpatterns = [
    path('index', IndexView.as_view()),
    path('add', AddView.as_view()),
]
