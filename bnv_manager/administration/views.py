from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from generic import ldap
from generic.mailcow import get_domains
from generic.models import AdvancedGroup, Domain


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
            return render(request, "generic/info.html", {"info": "This club already exists."})
        group.save()
        advanced = AdvancedGroup()
        advanced.group = group
        advanced.save()
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
            return render(request, "generic/info.html", {"info": "This club does not exist."})
        return redirect("/administration/clubs")


class ClubView(LoginRequiredMixin, TemplateView):
    template_name = "administration/club.html"

    def get(self, request, club="", *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "generic/notallowed.html")
        try:
            club = Group.objects.get(name=club)
            associated_domains = club.advancedgroup.associated_domains.all()
            other_domains = [x for x in get_domains() if x not in [y.name for y in associated_domains]]
        except Group.DoesNotExist:
            return render(request, "generic/info.html", {"info": "This club does not exist."})
        return render(
            request,
            self.template_name,
            {"associated_domains": associated_domains, "other_domains": other_domains, "club": club.name}
        )


class ClubAddDomain(LoginRequiredMixin, TemplateView):
    template_name = "generic/info.html"

    def post(self, request, club="", domain="", *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "generic/notallowed.html")
        try:
            domain = Domain.objects.get(name=domain)
            try:
                group = AdvancedGroup.objects.get(group__name=club)
                group.associated_domains.add(domain)
                group.save()
            except AdvancedGroup.DoesNotExist:
                return render(request, self.template_name, {"info": "Club does not exist."})
        except Domain.DoesNotExist:
            return render(request, self.template_name, {"info": "Domain does not exist."})
        return redirect(f"/administration/clubs/{club}")


class ClubRemoveDomain(LoginRequiredMixin, TemplateView):
    template_name = "generic/info.html"

    def post(self, request, club="", domain="", *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "generic/notallowed.html")
        try:
            domain = Domain.objects.get(name=domain)
            try:
                advanced_group = AdvancedGroup.objects.get(group__name=club)
                advanced_group.associated_domains.remove(domain)
                advanced_group.save()
            except AdvancedGroup.DoesNotExist:
                return render(request, self.template_name, {"info": "Club does not exist."})
        except Domain.DoesNotExist:
            return render(request, self.template_name, {"info": "Domain does not exist."})
        return redirect(f"/administration/clubs/{club}")


class AccountOverview(LoginRequiredMixin, TemplateView):
    template_name = "administration/accounts.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "generic/notallowed.html")
        return render(request, self.template_name)
