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
                "givenName": [bytes(request.POST["givenName"])],
                "sn": [bytes(request.POST["sn"])],
                "mail": [bytes(request.POST["mail"])],
                "MailQuota": [bytes(request.POST["quota"])],
                "objectClass": [bytes("BNVuser"), bytes("top")],
                "uid": [bytes(request.POST["uid"])],
                "Verein": [bytes(request.POST["verein"])],

            }
        )
        l.add_s(request.POST["uid"] + settings.LDAP_USER_DN, modlist=modlist)
        l.unbind_s()
        return render(request, self.template_name)
