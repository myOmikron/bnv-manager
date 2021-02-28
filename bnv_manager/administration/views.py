from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from generic import ldap
from generic.mailcow import get_domains


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "administration/index.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "generic/notallowed.html")
        return render(request, self.template_name)


class DomainView(LoginRequiredMixin, TemplateView):
    template_name = "administration/domain.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "generic/notallowed.html")
        domain_list = get_domains()
        club_list = Group.objects.filter(name__regex=r"^(?!.*superuser).*$")
        return render(
            request,
            self.template_name,
            {
                "domain_list": domain_list,
                "club_list": club_list
            }
        )


class ClubOverview(LoginRequiredMixin, TemplateView):
    template_name = "administration/club_overview.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "generic/notallowed.html")

        club_list = Group.objects.filter(name__regex=r"^(?!.*superuser).*$")
        return render(request, self.template_name, {"club_list": club_list})


class ClubAddView(LoginRequiredMixin, TemplateView):
    template_name = "generic/notallowed.html"

    def post(self, request):
        name = request.POST["name"]
        if not request.user.is_superuser:
            return render(request, "generic/notallowed.html")
        group, created = Group.objects.get_or_create(name=name)
        if not created:
            return render(request, "generic/info.html", {"message": "This group already exists."})
        group.save()
        ldap.add_club(name)
        return redirect("/administration/clubs")


class ClubDeleteView(LoginRequiredMixin, TemplateView):
    template_name = "generic/notallowed.html"

    def post(self, request, name="", *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "generic/notallowed.html")
        try:
            group = Group.objects.get(name=name)
            group.delete()
        except Group.DoesNotExist:
            return render(request, "generic/info.html", {"message": "This club does not exist."})
        return redirect("/administration/clubs")


class ClubView(LoginRequiredMixin, TemplateView):
    template_name = "administration/club.html"

    def get(self, request, club="", *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "generic/notallowed.html")
        return render(request, self.template_name)


class AccountOverview(LoginRequiredMixin, TemplateView):
    template_name = "administration/accounts.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "generic/notallowed.html")
        return render(request, self.template_name)
