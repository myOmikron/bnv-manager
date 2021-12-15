import time

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView

import utils.ldap
import utils.mailcow


class ClubInitial(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        is_club_admin = any([x for x in utils.ldap.get_club_admins() if x["username"] == request.user.username])
        if not is_club_admin:
            return render(request, "utils/referrer.html", {"msg": "You are not allowed to access this page!"})
        club = utils.ldap.get_club_for_user(request.user.ldap_user.dn)
        if club:
            return redirect(f"/club-management/{club.split(',')[0].split('=')[1]}/")
        return render(request, "utils/referrer.html", {"msg": "Nothing here :C"})


class ClubDashboard(LoginRequiredMixin, TemplateView):
    template_name = "club/dashboard.html"

    def get(self, request, sid=None, *args, **kwargs):
        is_club_admin = any([x for x in utils.ldap.get_club_admins() if x["username"] == request.user.username])
        if not is_club_admin:
            return render(request, "utils/referrer.html", {"msg": "You are not allowed to access this page!"})
        if sid != utils.ldap.get_club_for_user(request.user.ldap_user.dn).split(',')[0].split('=')[1]:
            return render(request, "utils/referrer.html", {"msg": "You are not allowed to access this page!"})
        users = utils.ldap.get_club_users(sid)
        users = sorted(users, key=lambda x: x["username"])
        return render(request, self.template_name, {"is_club_admin": is_club_admin, "users": users})
