from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "management/index.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
