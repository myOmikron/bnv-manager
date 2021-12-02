from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView

from generic.models import Club


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "admin/admin_management.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "utils/referrer.html", {"msg": "You are not allowed to use this!"})
        clubs = Club.objects.all()
        return render(request, self.template_name, {"clubs": clubs})


class CreateClubView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "utils/referrer.html", {"msg": "You are not allowed to use this!"})
        club = request.POST["club"]
        new_club, created = Club.objects.get_or_create(name=club)
        if not created:
            return render(request, "utils/referrer.html", {"msg": "There is already a club with that name!"})
        return redirect("/admin-management/")


class DeleteClubView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "utils/referrer.html", {"msg": "You are not allowed to use this!"})
        club_id = request.POST["club"]
        try:
            club = Club.objects.get(id=club_id)
            club.delete()
        except Club.DoesNotExist:
            return render(request, "utils/referrer.html", {"msg": f"The club with the id {club_id} does not exist!"})
        return redirect("/admin-management/")


class AdminClubManagement(LoginRequiredMixin, TemplateView):
    template_name = "admin/admin_club_management.html"

    def get(self, request, club_id=None, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, "utils/referrer.html", {"msg": "You are not allowed to use this page!"})
        try:
            club = Club.objects.get(id=club_id)
        except Club.DoesNotExist:
            return render(request, "utils/referrer.html", {"msg": f"Club with id {club_id} does not exist!"})
        return render(request, self.template_name, {"club": club})
