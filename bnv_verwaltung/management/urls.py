from django.urls import path

from management.views import IndexView

urlpatterns = [
    path('index', IndexView.as_view()),
]
