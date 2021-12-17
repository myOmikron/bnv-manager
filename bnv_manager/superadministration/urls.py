from django.urls import path

from superadministration.views import *


urlpatterns = [
    path('', DashboardView.as_view()),
    path('createClub', CreateClubView.as_view()),
    path('deleteClub', DeleteClubView.as_view()),

    path('removeClubAdmin', RemoveClubAdminFromClub.as_view()),
    path('addClubAdmin', AddClubAdminToClub.as_view()),

    path('createClubAdmin', CreateClubAdmin.as_view()),

    path('addDomain', AddDomain.as_view()),
    path('removeDomain', RemoveDomain.as_view()),

    path('resetPassword', AdminResetPassword.as_view()),

    path('clubs/<str:club_id>/', AdminClubManagement.as_view()),
]
