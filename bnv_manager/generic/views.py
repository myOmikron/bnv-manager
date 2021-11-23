from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView


class Login(LoginView):
    template_name = "auth/login.html"


class Logout(LoginRequiredMixin, LogoutView):
    pass
