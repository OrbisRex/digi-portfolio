from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.contrib.auth.models import User

from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView

from .models import Member
from .models import Subject
from .models import Topic
from .models import Set

from .forms import SubjectForm
from .forms import TopicForm
from .forms import SetForm


class IndexView(PermissionRequiredMixin, TemplateView):
    """Conbined view for basic settings."""
    
    permission_required = ('settings.view_subject', 'settings.view_topic', 'settings.view_set')
    template_name = "index.html"

    def get(self, request):
        ## Subject and topic section
        if self.get_current_user().member.role == Member.Roles.ADMIN:
            subjects = self.all_subjects()
            topics = self.all_topics()
            sets = self.all_sets()
        else:
            subjects = self.filter_subjects_by_owner()
            topics = self.filter_topics_by_owner()
            sets = self.filter_sets_by_owner()

        ## Render all data
        context = {'subjects':subjects, 'topics':topics, 'sets':sets}
        return render(request, 'settings/index.html', context)
    
    ##Service methods
    def get_current_user(self):
        return User.objects.get(pk=self.request.user.id)

    def all_subjects(self):
        return Subject.objects.all().order_by('name')

    def all_topics(self):
        return Topic.objects.all().order_by('heading')

    def all_sets(self):
        return Set.objects.all().order_by('name')

    def filter_subjects_by_owner(self):
        return Subject.objects.filter(lead=self.request.user.id).order_by('name')

    def filter_topics_by_owner(self):
        return Topic.objects.filter(author=self.request.user.id).order_by('heading')

    def filter_sets_by_owner(self):
        return Set.objects.filter(lead=self.request.user.id).order_by('name')
        

class SubjectView(PermissionRequiredMixin, UpdateView):
    """Creat new or edit existing subject."""
    
    model = Subject
    form_class = SubjectForm
    permission_required = ('settings.change_subject') # If user can change => add
    template_name = "settings/subject.html"
    
    def get(self, request, subject_id=None):
        # Test GET parameters to edit or inser data
        try:
            subject = self.model.objects.get(pk = subject_id)
            form = self.form_class(request=request, initial={'name':subject.name, 'lead':[i.id for i in subject.lead.all()]})
        except self.model.DoesNotExist:
            subject = None
            form = self.form_class(request=request)

        context = {'subject' : subject, 'form' : form}
        return render(request, self.template_name, context)

    def post(self, request, subject_id=None):
        form = self.form_class(request.POST, request=request)
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

        return HttpResponseRedirect(reverse("settings:index", fragment='#subject'))
        

class TopicView(PermissionRequiredMixin, UpdateView):
    """Creat new or edit existing topic."""
    
    model = Topic
    form_class = TopicForm
    permission_required = ('settings.change_topic')
    template_name='settings/topic.html'
    default_redirect = '/'
    
    def get(self, request, topic_id=None):
        # Test GET parameters to edit or inser data
        try:
            topic = self.model.objects.get(pk = topic_id)
            form = self.form_class(request=request, initial={'heading':topic.heading, 'author':topic.author, 'text':topic.text})
        except self.model.DoesNotExist:
            topic = None
            form = self.form_class(request=request, initial={'author' : request.user.id})

        context = {'topic' : topic, 'form' : form}
        return render(request, self.template_name, context)

    def post(self, request, topic_id=None):
        form = self.form_class(request.POST, request=request)
        try:
            # Prepare data to save
            topic = self.model.objects.get(pk = topic_id)
            
            if form.is_valid():
                topic.heading = form.cleaned_data['heading']
                topic.author = User.objects.get(pk=request.user.id)
                topic.save()
        except self.model.DoesNotExist:
            # New Topic form
            if form.is_valid():
                topic = form.save(commit=False)
                topic.save()
                form.save_m2m()
            
        return HttpResponseRedirect(reverse("settings:index", fragment='#topic'))
        

class SetView(PermissionRequiredMixin, UpdateView):
    """Creat new or edit existing set."""
    
    model = Set
    form_class = SetForm
    permission_required = ('settings.change_set') # If user can change => add
    template_name = "settings/set.html"
    
    def get(self, request, set_id=None):
        # Test GET parameters to edit or inser data
        try:
            set = self.model.objects.get(pk = set_id)
            form = self.form_class(request=request, initial={'name':set.name, 'type':set.type, 'lead':[i.id for i in set.lead.all()]})
        except self.model.DoesNotExist:
            set = None
            form = self.form_class(request=request)

        context = {'set' : set, 'form' : form}
        return render(request, self.template_name, context)

    def post(self, request, set_id=None):
        form = self.form_class(request.POST, request=request)
        try:
            # Prepare data to save
            set = self.model.objects.get(pk = set_id)

            if form.is_valid():
                set.name = form.cleaned_data['name']
                set.type = form.cleaned_data['type']
                set.lead.set(form.cleaned_data['lead'])
                set.save()           
        except self.model.DoesNotExist:
            # New Set form
            if form.is_valid():
                set = form.save(commit=False)
                set.save()
                form.save_m2m()

        return HttpResponseRedirect(reverse("settings:index", fragment='#set'))
