from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.template import loader

from django.views.generic import TemplateView
from django.conf import settings

from settings.models import Staff


class IndexView(TemplateView):
    """Homepage"""
        
    template_name = "index.html"

    def get(self, request):
        context = {'wolcome':'DIGI Portfolio'}
        return render(request, 'core/index.html', context)


class DashboardView(TemplateView):
    """Homepage for all users after sign in."""
        
    template_name = "index.html"

    def get_current_user(self):
        return Staff.objects.get(pk=self.request.user.id)

    def get(self, request):
        
        try:
            loged_as = self.get_current_user()
        except Staff.DoesNotExist:
            loged_as = None
            #error_msg = "You are not authorised to operate the system. Contact the administrator to grant you access."

        ## Render all data
        context = {'loged_as':loged_as}
        return render(request, 'core/dashboard.html', context)
