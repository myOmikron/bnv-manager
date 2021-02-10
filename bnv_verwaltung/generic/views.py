from django.contrib.auth.views import LoginView, LogoutView


class Login(LoginView):
    template_name = "generic/login.html"


class Logout(LogoutView):
    pass
