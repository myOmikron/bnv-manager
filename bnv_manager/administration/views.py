from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group, User
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django_auth_ldap.backend import LDAPBackend

from generic import ldap
from generic.mailcow import get_domains
from generic.models import AdvancedGroup, Domain, AdvancedUser


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
            associated_manager = [x.user for x in AdvancedUser.objects.all() if not x.user.is_superuser and club.name in [y.group.name for y in x.associated_clubs.all()]]
            other_manager = [x.user for x in AdvancedUser.objects.all() if not x.user.is_superuser and club.name not in [y.group.name for y in x.associated_clubs.all()]]
        except Group.DoesNotExist:
            return render(request, "generic/info.html", {"info": "This club does not exist."})
        return render(
            request,
            self.template_name,
            {"associated_domains": associated_domains, "other_domains": other_domains, "club": club.name,
             "associated_manager": associated_manager, "other_manager": other_manager}
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


class ClubAddManager(LoginRequiredMixin, TemplateView):
    template_name = "generic/info.html"

    def post(self, request, club="", manager="", *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "generic/notallowed.html")
        try:
            manager = AdvancedUser.objects.get(user__username=manager)
            try:
                group = AdvancedGroup.objects.get(group__name=club)
                manager.associated_clubs.add(group)
                manager.save()
            except AdvancedGroup.DoesNotExist:
                return render(request, self.template_name, {"info": "Club does not exist."})
        except AdvancedUser.DoesNotExist:
            return render(request, self.template_name, {"info": "Manager does not exist."})
        return redirect(f"/administration/clubs/{club}")


class ClubRemoveManager(LoginRequiredMixin, TemplateView):
    template_name = "generic/info.html"

    def post(self, request, club="", manager="", *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "generic/notallowed.html")
        try:
            manager = AdvancedUser.objects.get(user__username=manager)
            try:
                advanced_group = AdvancedGroup.objects.get(group__name=club)
                manager.associated_clubs.remove(advanced_group)
                manager.save()
            except AdvancedGroup.DoesNotExist:
                return render(request, self.template_name, {"info": "Club does not exist."})
        except AdvancedUser.DoesNotExist:
            return render(request, self.template_name, {"info": "Manager does not exist."})
        return redirect(f"/administration/clubs/{club}")


class AccountOverview(LoginRequiredMixin, TemplateView):
    template_name = "administration/accounts.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "generic/notallowed.html")
        return render(
            request, self.template_name,
            {"users": User.objects.all(),
             "user_names": [x.username for x in User.objects.all()]}
        )


class AccountDelete(LoginRequiredMixin, TemplateView):
    template_name = "generic/notallowed.html"

    def post(self, request, username="", *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, self.template_name)
        try:
            user = User.objects.get(username=username)
            ldap.del_manager_user(username, user.is_superuser)
            user.delete()
        except AdvancedUser.DoesNotExist:
            return render(request, "generic/info.html", {"info", "User does not exist."})
        return redirect(f"/administration/accounts")


class AccountAdd(LoginRequiredMixin, TemplateView):
    template_name = "generic/notallowed.html"

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, self.template_name)
        ldap.add_manager_user(
            request.POST["username"], request.POST["firstname"], request.POST["lastname"], request.POST["mail"],
            request.POST["password"], is_superuser=True if "superadmin" in request.POST else False
        )
        LDAPBackend().populate_user(request.POST["username"])
        if "superadmin" not in request.POST:
            user = User.objects.get(username=request.POST["username"])
            advanced, created = AdvancedUser.objects.get_or_create(user=user)
            if not created:
                return render(request, "generic/info.html", {"info": "User already exists."})
            advanced.save()
        return redirect(f"/administration/accounts")
