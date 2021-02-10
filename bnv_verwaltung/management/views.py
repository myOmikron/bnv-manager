import ldap
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "management/index.html"

    def get(self, request, *args, **kwargs):
        from bnv_verwaltung import settings
        l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
        l.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
        users = l.search_s(settings.LDAP_USER_DN, ldap.SCOPE_SUBTREE, settings.LDAP_USER_FILTER)
        l.unbind_s()
        return render(request, self.template_name, {"users": users})


class AddView(LoginRequiredMixin, TemplateView):
    template_name = "management/add.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        from bnv_verwaltung import settings
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

            }
        )
        l.add_s(request.POST["uid"] + settings.LDAP_USER_DN, modlist=modlist)
        l.unbind_s()
        return render(request, self.template_name)
