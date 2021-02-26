from django.urls import path

from management.views import IndexView, AddView, DeleteView

urlpatterns = [
    path('index', IndexView.as_view()),
    path('add', AddView.as_view()),
    path('delete/<str:k>', DeleteView.as_view()),
]
