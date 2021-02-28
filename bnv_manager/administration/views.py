from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

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
        group_list = Group.objects.filter(name__regex=r"^(?!.*superuser).*$")
        return render(
            request,
            self.template_name,
            {
                "domain_list": domain_list,
                "group_list": group_list
            }
        )


class GroupView(LoginRequiredMixin, TemplateView):
    template_name = "administration/groups.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "generic/notallowed.html")
        group_list = Group.objects.filter(name__regex=r"^(?!.*superuser).*$")
        return render(request, self.template_name, {"group_list": group_list})


class GroupAddView(LoginRequiredMixin, TemplateView):
    template_name = "generic/notallowed.html"

    def post(self, request):
        name = request.POST["name"]
        if not request.user.is_superuser:
            return render(request, "generic/notallowed.html")
        group, created = Group.objects.get_or_create(name=name)
        if not created:
            return render(request, "generic/info.html", {"message": "This group already exists."})
        group.save()
        return redirect("/administration/groups")


class GroupDeleteView(LoginRequiredMixin, TemplateView):
    template_name = "generic/notallowed.html"

    def post(self, request, name="", *args, **kwargs):
        print(request.user)
        if not request.user.is_superuser:
            return render(request, "generic/notallowed.html")
        try:
            group = Group.objects.get(name=name)
            group.delete()
        except Group.DoesNotExist:
            return render(request, "generic/info.html", {"message": "This group does not exist."})
        return redirect("/administration/groups")
