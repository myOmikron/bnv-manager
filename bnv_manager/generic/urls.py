from django.urls import path

from generic.views import *


urlpatterns = [
    path('login', Login.as_view()),
    path('logout', Logout.as_view()),
    path('', DashboardView.as_view()),

    # Account functionality
    path('user/resetPassword', ResetPassword.as_view()),
    path('user/deleteAlias', DeleteAlias.as_view()),
    path('user/createAlias', CreateAlias.as_view()),
]
