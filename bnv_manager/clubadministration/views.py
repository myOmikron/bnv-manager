from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView

import utils.ldap
import utils.mailcow
import utils.generic
from bnv_manager import settings
from generic.models import Club


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
        return render(request, self.template_name, {"is_club_admin": is_club_admin, "users": users, "club": sid})


class ClubResetPassword(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        is_club_admin = any([x for x in utils.ldap.get_club_admins() if x["username"] == request.user.username])
        if not is_club_admin:
            return render(request, "utils/referrer.html", {"msg": "You are not allowed to access this page!"})
        if request.POST["club"] != utils.ldap.get_club_for_user(request.user.ldap_user.dn).split(',')[0].split('=')[1]:
            return render(request, "utils/referrer.html", {"msg": "You are not allowed to access this page!"})


class ClubCreateUser(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        is_club_admin = any([x for x in utils.ldap.get_club_admins() if x["username"] == request.user.username])
        if not is_club_admin:
            return render(request, "utils/referrer.html", {"msg": "You are not allowed to access this page!"})
        club = request.POST["club"]
        if club != utils.ldap.get_club_for_user(request.user.ldap_user.dn).split(',')[0].split('=')[1]:
            return render(request, "utils/referrer.html", {"msg": "You are not allowed to access this page!"})
        firstname = request.POST["firstname"]
        surname = request.POST["surname"]
        mail = request.POST["mail"]
        domain = mail.split("@")[1].lower()
        try:
            club_object = Club.objects.get(abbreviation=club)
        except Club.DoesNotExist:
            return render(request, "utils/referrer.html", {"msg": "Club does not exist!"})
        if domain not in [x.domain for x in club_object.associated_domains.all()]:
            return render(request, "utils/referrer.html", {"msg": "This domain isn't associated with your club!"})
        if not utils.ldap.check_unique_mail(mail):
            return render(
                request, "utils/referrer.html", {"msg": "This mail has already been registered by another user"}
            )
        username = utils.ldap.generate_username(firstname, surname)
        password = request.POST["initialPassword"]
        if not utils.generic.enforce_password_policy(password):
            return render(
                request, "utils/referrer.html",
                {"msg": "Your password did not meet the requirements: More than 12 characters, min. one special character"}
            )
        dn = utils.ldap.add_user(username, firstname, surname, mail, password, settings.AUTH_LDAP_USER_BASE)
        utils.ldap.add_user_to_group(dn, club)
        utils.mailcow.add_mailbox(firstname, surname, mail, password)
        return render(
            request, "utils/user_creation_summary.html",
            {
                "referer": request.META["HTTP_REFERER"],
                "username": username,
                "firstname": firstname,
                "surname": surname,
                "mail": mail
            }
        )

