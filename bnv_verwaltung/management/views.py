import hashlib
from base64 import b64encode
import os

import ldap

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView

from bnv_verwaltung import settings


def make_secret(password):
    salt = os.urandom(4)
    h = hashlib.sha1(password.encode("utf-8"))
    h.update(salt)
    return "{SSHA}".encode("utf-8") + b64encode(h.digest() + salt)


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "management/index.html"

    def get(self, request, *args, **kwargs):
        l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
        l.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
        ldap_users = l.search_s(settings.LDAP_USER_DN,
                                ldap.SCOPE_SUBTREE,
                                settings.LDAP_USER_FILTER,
                                attrlist=["givenName", "sn", "mail", "MailQuota", "Verein", "uid"])
        l.unbind_s()
        users = []
        for user in ldap_users:
            x = {
                "uid": user[1]["uid"][0].decode("utf-8"),
                "givenName": user[1]["givenName"][0].decode("utf-8"),
                "sn": user[1]["givenName"][0].decode("utf-8"),
                "mail": user[1]["givenName"][0].decode("utf-8"),
                "quota": user[1]["givenName"][0].decode("utf-8"),
                "Verein": user[1]["givenName"][0].decode("utf-8"),
            }
            users.append(x)
        return render(request, self.template_name, {"users": users})


class AddView(LoginRequiredMixin, TemplateView):
    template_name = "management/add.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        import ldap.modlist
        l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
        l.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
        modlist = ldap.modlist.addModlist(
            {
                "givenName": [request.POST["givenName"].encode("utf-8")],
                "sn": [request.POST["sn"].encode("utf-8")],
                "mail": [request.POST["mail"].encode("utf-8")],
                "MailQuota": [request.POST["quota"].encode("utf-8")],
                "objectClass": ["BNVuser".encode("utf-8"), "top".encode("utf-8")],
                "uid": [request.POST["uid"].encode("utf-8")],
                "Verein": [request.POST["verein"].encode("utf-8")],
                "userPassword": [make_secret(request.POST['pw'])],
            }
        )
        l.add_s(f"uid={request.POST['uid']},{settings.LDAP_USER_DN}", modlist=modlist)
        l.unbind_s()
        return render(request, self.template_name)


class DeleteView(LoginRequiredMixin, View):

    def post(self, request, k="", *args, **kwargs):
        l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
        l.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
        l.delete_s(f"uid={k},{settings.LDAP_USER_DN}")
        l.unbind_s()
        return redirect("/management/index")
