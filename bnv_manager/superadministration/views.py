import re

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.utils.translation import gettext as _

from bnv_manager import settings
from generic.models import Club, Domain

import utils.ldap
import utils.mailcow
import utils.generic


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "admin/admin_management.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "utils/referrer.html", {"msg": _("You are not allowed to use this!")})
        clubs = Club.objects.all()
        return render(request, self.template_name, {"clubs": clubs})


class CreateClubView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "utils/referrer.html", {"msg": _("You are not allowed to use this!")})
        club = request.POST["club"]
        abbreviation = request.POST["abbreviation"]
        if not re.match(r"^[a-zA-Z0-9]+$", abbreviation):
            return render(request, "utils/referrer.html", {"msg": _("Abbreviation contains an disallowed character")})
        new_club, created = Club.objects.get_or_create(name=club)
        if not created:
            return render(request, "utils/referrer.html", {"msg": _("There is already a club with that name!")})
        new_club.abbreviation = abbreviation
        new_club.save()
        return redirect("/admin-management/")


class DeleteClubView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "utils/referrer.html", {"msg": _("You are not allowed to use this!")})
        club_id = request.POST["club"]
        try:
            club = Club.objects.get(id=club_id)
            club_users = utils.ldap.get_club_users(club.abbreviation, search_base=settings.LDAP_GLOBAL_SEARCH_BASE)
            for user in club_users:
                utils.ldap.del_dn(f"cn={club.abbreviation},{settings.LDAP_GROUP_DN}")
                utils.ldap.del_dn(user["dn"])
                if ",".join(user["dn"].split(",")[1:]) == settings.AUTH_LDAP_USER_BASE:
                    utils.mailcow.del_mailbox(user["mail"])
                elif ",".join(user["dn"].split(",")[1:]) == settings.AUTH_LDAP_CLUB_ADMIN_BASE:
                    utils.mailcow.del_domain_admin(user["username"])
            club.delete()
        except Club.DoesNotExist:
            return render(request, "utils/referrer.html", {"msg": _("The club does not exist!")})
        return redirect("/admin-management/")


class AdminClubManagement(LoginRequiredMixin, TemplateView):
    template_name = "admin/admin_club_management.html"

    def get(self, request, club_id=None, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "utils/referrer.html", {"msg": _("You are not allowed to use this page!")})
        try:
            club = Club.objects.get(id=club_id)
        except Club.DoesNotExist:
            return render(request, "utils/referrer.html", {"msg": _("Club does not exist!")})
        club_admins = utils.ldap.get_club_admins(club=club.abbreviation)
        other_club_admins = utils.ldap.get_club_admins(club=club.abbreviation, invert=True)

        all_domains = utils.mailcow.get_domains()
        domains = club.associated_domains.all()
        other_domains = []
        for x in all_domains:
            if x.domain not in [y.domain for y in domains]:
                other_domains.append(x)
        return render(request, self.template_name, {
            "club": club,
            "domains": domains,
            "other_domains": other_domains,
            "club_admins": club_admins,
            "other_club_admins": other_club_admins
        })


class RemoveClubAdminFromClub(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "utils/referrer.html", {"msg": _("You are not allowed to use this page!")})
        abbreviation = request.POST["abbreviation"]
        dn = request.POST["dn"]
        domain_admins = utils.mailcow.get_domain_admins()
        username = dn.split(",")[0].split("=")[1]
        if username in [x["username"] for x in domain_admins]:
            utils.mailcow.del_domain_admin(username)
        utils.ldap.remove_users_from_group([dn], abbreviation)
        return redirect(request.META["HTTP_REFERER"])


class AddClubAdminToClub(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "utils/referrer.html", {"msg": _("You are not allowed to use this page!")})
        dn = request.POST["dn"]
        abbreviation = request.POST["abbreviation"]
        try:
            club = Club.objects.get(abbreviation=abbreviation)
        except Club.DoesNotExist:
            return render(request, "utils/referrer.html", {"msg": _("Club does not exist")})
        utils.ldap.add_users_to_group([dn], abbreviation)
        if any(club.associated_domains.all()):
            utils.mailcow.create_domain_admin(
                username=dn.split(",")[0].split("=")[1],
                domains=[x.domain for x in club.associated_domains.all()],
                password=utils.ldap.get_hash_for_user(dn)
            )
        return redirect(request.META["HTTP_REFERER"])


class CreateClubAdmin(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "utils/referrer.html", {"msg": _("You are not allowed to use this page!")})
        firstname = request.POST["firstname"]
        surname = request.POST["surname"]
        mail = request.POST["mail"]
        password = request.POST["password"]
        if not firstname or not surname or not mail or not password:
            return render(request, "utils/referrer.html", {"msg": _("Please fill out every field")})
        username = utils.ldap.generate_username(firstname, surname)
        utils.ldap.add_user(username, firstname, surname, mail, password, settings.AUTH_LDAP_CLUB_ADMIN_BASE)
        return render(request, "utils/user_creation_summary.html", {
            "referer": request.META["HTTP_REFERER"],
            "username": username,
            "firstname": firstname,
            "surname": surname,
            "mail": mail
        })


class AddDomain(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "utils/referrer.html", {"msg": _("You are not allowed to use this page!")})
        domain_name = request.POST["domain"]
        club_id = request.POST["club"]
        try:
            club = Club.objects.get(id=club_id)
        except Club.DoesNotExist:
            return render(request, "utils/referrer.html", {"msg": _("Club does not exist!")})
        try:
            domain = Domain.objects.get(domain=domain_name)
        except Domain.DoesNotExist:
            return render(request, "utils/referrer.html", {"msg": _("There is no such domain")})
        club_admins = utils.ldap.get_club_admins(club.name)
        club_admin_usernames = [x["username"] for x in club_admins]
        domain_admins = [x for x in utils.mailcow.get_domain_admins() if x["username"] in club_admin_usernames]
        for x in domain_admins:
            utils.mailcow.set_domain_for_domain_admin(x["username"], [*x["selected_domains"], domain.domain])
        associated_domains = club.associated_domains.all()
        if not any(associated_domains):
            for x in club_admins:
                utils.mailcow.create_domain_admin(x["username"], domain.domain, utils.ldap.get_hash_for_user(x["dn"]))
        club.associated_domains.add(domain)
        return redirect(request.META["HTTP_REFERER"])


class RemoveDomain(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "utils/referrer.html", {"msg": _("You are not allowed to use this page!")})
        domain_name = request.POST["domain"]
        club_id = request.POST["club"]
        try:
            club = Club.objects.get(id=club_id)
        except Club.DoesNotExist:
            return render(request, "utils/referrer.html", {"msg": _("Club does not exist!")})
        try:
            domain = Domain.objects.get(domain=domain_name)
        except Domain.DoesNotExist:
            return render(request, "utils/referrer.html", {"msg": _("There is no such domain")})
        club.associated_domains.remove(domain)
        club_admins = utils.ldap.get_club_admins(club.name)
        domains = [x.domain for x in club.associated_domains.all()]
        if any(domains):
            for x in club_admins:
                utils.mailcow.set_domain_for_domain_admin(x["username"], domains)
        else:
            for x in club_admins:
                utils.mailcow.del_domain_admin(x["username"])
        return redirect(request.META["HTTP_REFERER"])


class AdminResetPassword(LoginRequiredMixin, TemplateView):
    template_name = "utils/admin_password_reset.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "utils/referrer.html", {"msg": _("You are not allowed to access this page!")})
        username = request.GET["username"]
        return render(request, self.template_name, {"username": username})

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "utils/referrer.html", {"msg": _("You are not allowed to access this page!")})
        username = request.POST["username"]
        dn = f"cn={username},{settings.AUTH_LDAP_CLUB_ADMIN_BASE}"
        password = request.POST["password"]
        if not utils.generic.enforce_password_policy(password):
            return render(
                request, "utils/referrer.html",
                {"msg": _(
                    "Your password did not meet the requirements: More than 11 characters, min. one special character")}
            )
        utils.ldap.set_password(dn, password)
        return redirect("/admin-management/")
