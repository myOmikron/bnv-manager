import re

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView

from bnv_manager import settings
from generic.models import Club

import utils.ldap


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "admin/admin_management.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "utils/referrer.html", {"msg": "You are not allowed to use this!"})
        clubs = Club.objects.all()
        return render(request, self.template_name, {"clubs": clubs})


class CreateClubView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "utils/referrer.html", {"msg": "You are not allowed to use this!"})
        club = request.POST["club"]
        abbreviation = request.POST["abbreviation"]
        if not re.match(r"^[a-zA-Z0-9]+$", abbreviation):
            return render(request, "utils/referrer.html", {"msg": "Abbreviation contains an disallowed character"})
        new_club, created = Club.objects.get_or_create(name=club)
        if not created:
            return render(request, "utils/referrer.html", {"msg": "There is already a club with that name!"})
        new_club.abbreviation = abbreviation
        new_club.save()
        return redirect("/admin-management/")


class DeleteClubView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "utils/referrer.html", {"msg": "You are not allowed to use this!"})
        club_id = request.POST["club"]
        try:
            club = Club.objects.get(id=club_id)
            club.delete()
        except Club.DoesNotExist:
            return render(request, "utils/referrer.html", {"msg": f"The club with the id {club_id} does not exist!"})
        return redirect("/admin-management/")


class AdminClubManagement(LoginRequiredMixin, TemplateView):
    template_name = "admin/admin_club_management.html"

    def get(self, request, club_id=None, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "utils/referrer.html", {"msg": "You are not allowed to use this page!"})
        try:
            club = Club.objects.get(id=club_id)
        except Club.DoesNotExist:
            return render(request, "utils/referrer.html", {"msg": f"Club with id {club_id} does not exist!"})
        club_admins = utils.ldap.get_club_admins(club=club.abbreviation)
        other_club_admins = utils.ldap.get_club_admins(club=club.abbreviation, invert=True)
        return render(request, self.template_name, {
            "club": club,
            "club_admins": club_admins,
            "other_club_admins": other_club_admins
        })


class RemoveClubAdminFromClub(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "utils/referrer.html", {"msg": "You are not allowed to use this page!"})
        utils.ldap.remove_users_from_group(
            [request.POST["dn"]],
            request.POST["club"]
        )
        return redirect(request.META["HTTP_REFERER"])


class AddClubAdminToClub(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "utils/referrer.html", {"msg": "You are not allowed to use this page!"})
        dn = request.POST["dn"]
        abbreviation = request.POST["abbreviation"]
        utils.ldap.add_users_to_group([dn], abbreviation)
        return redirect(request.META["HTTP_REFERER"])


class CreateClubAdmin(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "utils/referrer.html", {"msg": "You are not allowed to use this page!"})
        firstname = request.POST["firstname"]
        surname = request.POST["surname"]
        mail = request.POST["mail"]
        password = request.POST["password"]
        if not firstname or not surname or not mail or not password:
            return render(request, "utils/referrer.html", {"msg": "Please fill out every field"})
        username = utils.ldap.generate_username(firstname, surname)
        utils.ldap.add_user(username, firstname, surname, mail, password, settings.AUTH_LDAP_CLUB_ADMIN_BASE)
        return render(request, "utils/user_creation_summary.html", {
            "referer": request.META["HTTP_REFERER"],
            "username": username,
            "firstname": firstname,
            "surname": surname,
            "mail": mail
        })
