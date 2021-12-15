from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView


import utils.ldap
import utils.mailcow


class ClubDashboard(LoginRequiredMixin, TemplateView):
    template_name = "club/dashboard.html"

    def get(self, request, *args, **kwargs):
        is_club_admin = any([x for x in utils.ldap.get_club_admins() if x["username"] == request.user.username])
        if not is_club_admin:
            return render(request, "utils/referrer.html", {"msg": "You are not allowed to access this page!"})
        return render(request, self.template_name, {})
