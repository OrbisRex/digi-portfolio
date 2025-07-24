from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.template import loader

from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView
from django.conf import settings

from .models import Member
from .models import Subject
from .models import Topic
from .forms import SubjectForm
from .forms import TopicForm


class IndexView(PermissionRequiredMixin, TemplateView):
    """Conbined view for basic settings."""
    
    permission_required = ('settings.view_subject', 'settings.view_topic', 'settings.view_group')
    template_name = "index.html"

    def get(self, request):
        ## Subject section
        subjects = Subject.objects.all().order_by('name')

        ## Topic section
        topics = Topic.objects.all().order_by('heading')
        
        ## Render all data
        context = {'subjects':subjects, 'topics':topics}
        return render(request, 'settings/index.html', context)


class SubjectView(PermissionRequiredMixin, UpdateView):
    """Creat new or edit existing subject."""
    
    model = Subject
    form_class = SubjectForm
    permission_required = ('settings.add_subject', 'settings.change_subject')
    template_name = "settings/subject.html"
    
    def get(self, request, subject_id=None):
        # Test GET parameters to edit or inser data
        try:
            subject = self.model.objects.get(pk = subject_id)
            form = self.form_class(initial={'name' : subject.name})
        except self.model.DoesNotExist:
            subject = None
            form = self.form_class()

        context = {'subject' : subject, 'form' : form}
        return render(request, self.template_name, context)

    def post(self, request, subject_id=None):
        form = self.form_class(request.POST)
        try:
            # Prepare data to save
            subject = self.model.objects.get(pk = subject_id)

            if form.is_valid():
                subject.name = form.cleaned_data['name']
                subject.lead.set(form.cleaned_data['lead'])
                subject.save()           
        except self.model.DoesNotExist:
            # New Subject form
            if form.is_valid():
                subject = form.save(commit=False)
                subject.save()
                form.save_m2m()

        return HttpResponseRedirect('{}#subject'.format(reverse("settings:index")))
        

class TopicView(PermissionRequiredMixin, UpdateView):
    """Creat new or edit existing topic."""
    
    model = Topic
    form_class = TopicForm
    permission_required = ('setting.add_topic', 'setting.change_topic')
    template_name='settings/topic.html'
    
    def get(self, request, topic_id=None):
        # Test GET parameters to edit or inser data
        try:
            topic = self.model.objects.get(pk = topic_id)
            form = self.form_class(None, initial={'heading' : topic.heading, 'author' : topic.author, 'text' : topic.text})
        except self.model.DoesNotExist:
            topic = None
            form = self.form_class()

        context = {'topic' : topic, 'form' : form}
        return render(request, self.template_name, context)

    def post(self, request, topic_id=None):
        form = self.form_class(request.POST)
        try:
            # Prepare data to save
            topic = self.model.objects.get(pk = topic_id)
            
            if form.is_valid():
                topic.heading = form.cleaned_data['heading']
                topic.author = Member.objects.get(pk=request.user.id) # Select box or automatic?? Use rather settings.AUTH_USER_MODEL??
                topic.save()
        except self.model.DoesNotExist:
            # New Topic form
            if form.is_valid():
                topic = form.save(commit=False)
                topic.save()
                form.save_m2m()
            
        return HttpResponseRedirect('{}#topic'.format(reverse("settings:index")))
        

class GroupView(PermissionRequiredMixin, TemplateView):
    """Creat new or edit existing group."""
        
    permission_required = ('setting.add_group', 'setting.change_group')
    template_name="group.html"
        
    def get(request, group_id):
        response = "Group details: %s."
        return HttpResponse(response % group_id)
