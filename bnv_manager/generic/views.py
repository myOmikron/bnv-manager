from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from django.views.generic import TemplateView


class Login(LoginView):
    template_name = "generic/login.html"


class Logout(LogoutView):
    pass


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "base.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
