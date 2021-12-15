from django.urls import path, include

import superadministration.urls
import clubadministration.urls
from generic.views import *


urlpatterns = [
    path('login', Login.as_view()),
    path('logout', Logout.as_view()),
    path('', DashboardView.as_view()),

    # Account functionality
    path('user/resetPassword', ResetPassword.as_view()),
    path('user/deleteAlias', DeleteAlias.as_view()),
    path('user/createAlias', CreateAlias.as_view()),

    # Other
    path('admin-management/', include(superadministration.urls)),
    path('club-management/', include(clubadministration.urls))
]
