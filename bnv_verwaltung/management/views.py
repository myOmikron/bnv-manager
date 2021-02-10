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
        users = l.search_s(settings.LDAP_USER_DN, ldap.SCOPE_SUBTREE)
        print(users)
        return render(request, self.template_name, {"users": users})
