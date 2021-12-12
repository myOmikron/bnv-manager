import re

from django.contrib.auth import authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView

from generic import models

import utils.ldap
import utils.mailcow


class Login(LoginView):
    template_name = "auth/login.html"


class Logout(LoginRequiredMixin, LogoutView):
    pass


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "account.html"

    def get(self, request, *args, **kwargs):
        is_club_admin = any([x for x in utils.ldap.get_club_admins() if x["username"] == request.user.username])
        aliases = utils.mailcow.get_aliases(request.user.ldap_user.attrs["mail"][0])
        return render(request, self.template_name, {"is_club_admin": is_club_admin, "aliases": aliases})


class ResetPassword(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        if authenticate(request, username=request.user.username, password=request.POST["oldPW"]):
            if request.POST["newPW"] != request.POST["repeatNewPW"]:
                return render(request, "utils/referrer.html", {"msg": "New password was not repeated correctly!"})
            if request.user.ldap_user:
                utils.ldap.set_password(request.user.ldap_user.dn, request.POST["newPW"])
            logout(request)
            return redirect("/login")
        else:
            return render(request, "utils/referrer.html", {"msg": "Your current credentials were incorrect!"})


class DeleteAlias(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        alias_id = int(request.POST["alias"][0])
        if alias_id in [x["id"] for x in utils.mailcow.get_aliases(request.user.ldap_user.attrs["mail"][0])]:
            utils.mailcow.del_alias(alias_id)
        else:
            return render(request, "utils/referrer.html", {"msg": "You don't have the permission to delete this alias"})
        return redirect("/")


class CreateAlias(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        alias = request.POST["alias"]
        if not re.match(r'\b[A-Za-z0-9._%+-]+\b', alias):
            return render(request, "utils/referrer.html", {"msg": "You entered an invalid front-part!"})
        user_mail = request.user.ldap_user.attrs["mail"][0]
        if alias in [
            x["address"].split("@")[0] for x
            in utils.mailcow.get_aliases(filter_domain=user_mail.split("@")[1])
        ]:
            return render(
                request, "utils/referrer.html",
                {"msg": "There is already an alias registered with that front-part!"}
            )
        if alias in [
            x[1]["mail"][0].decode("utf-8").split("@")[0] for x
            in utils.ldap.get_user()
            if x[1]["mail"][0].decode("utf-8").split("@")[1] == user_mail.split("@")[1]
        ]:
            return render(
                request, "utils/referrer.html",
                {"msg": "There is already a mailbox registered with that front-part!"}
            )
        utils.mailcow.add_alias(request.user.ldap_user.attrs["mail"][0], f"{alias}@{user_mail.split('@')[1]}")
        return redirect("/")
