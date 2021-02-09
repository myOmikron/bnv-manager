from django.urls import path

from administration.views import IndexView

urlpatterns = [
    path("index", IndexView.as_view())
]
