from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.contrib.auth.models import User

from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView

from .models import Member
from .models import Assignment
from .models import Subject
from .models import Topic

from .forms import AssignmentForm


class IndexView(PermissionRequiredMixin, TemplateView):
    """Conbined view of all assignments."""

    permission_required = ('projects.view_assignment', 'settings.view_member', 'settings.view_subject')
    template_name = "index.html"
    
    def get_current_user(self):
        try:
           return User.objects.get(pk=self.request.user.id)
        except:
            return None

    def get(self, request, subject_id=None, topic_id=None):
        ## Top section #####
        try:
            if self.get_current_user().member.role == Member.Roles.ADMIN:
                assignments = Assignment.objects.all()[:8]
            else:
                assignments = Assignment.get_assignments_by_teacher(user=self.request.user, limit=8)
                
        except Assignment.DoesNotExist:
            assignments = None
        
        ## Assignments by subject section #####
        # List of subjects for buttons
        if self.get_current_user().member.role == Member.Roles.ADMIN:
            subjects = Subject.objects.all()
        else:
            subjects = Subject.get_subjects_by_owner(self.get_current_user())
        
        # Select assignments
        try:
            selected_subject = Subject.objects.get(pk = subject_id)
            if self.get_current_user().member.role == Member.Roles.ADMIN:
                assignments_by_subject = Assignment.objects.filter(subject=subject_id)
            else:
                assignments_by_subject = Assignment.get_assignments_by_subject(user=self.request.user, id=subject_id)
        except Subject.DoesNotExist:
            selected_subject = None
            if self.get_current_user().member.role == Member.Roles.ADMIN:
                assignments_by_subject = Assignment.objects.all()[:8]
            else:
                assignments_by_subject = Assignment.get_assignments_by_teacher(self.get_current_user(), limit=8)
                
        ## Assignments by topic section #####
        # List of topics for buttons
        if self.get_current_user().member.role == Member.Roles.ADMIN:
            topics = Topic.objects.all()
        else:
            topics = Topic.get_topics_by_owner(self.request.user)
        
        # Select assignments
        try:
            selected_topic = Topic.objects.get(pk = topic_id)
            if self.get_current_user().member.role == Member.Roles.ADMIN:
                assignments_by_topic = Assignment.objects.filter(topic=topic_id)
            else:
                assignments_by_topic = Assignment.get_assignments_by_topic(user=self.request.user, id=topic_id)
        except Topic.DoesNotExist:
            selected_topic = None
            if self.get_current_user().member.role == Member.Roles.ADMIN:
                assignments_by_topic = Assignment.objects.all()[:8]
            else:
                assignments_by_topic = Assignment.get_assignments_by_teacher(user=self.request.user, limit=8)

        # Render all data
        context = {'assignments':assignments, 
                   'subjects':subjects, 
                   'topics':topics, 
                   'selected_subject':selected_subject, 
                   'assignments_by_subject':assignments_by_subject, 
                   'selected_topic':selected_topic, 
                   'assignments_by_topic':assignments_by_topic
                   }
        return render(request, 'assignment/index.html', context)


class NewEditView(PermissionRequiredMixin, UpdateView):
    """Creat new or edit existing assignment."""

    model = Assignment
    form_class = AssignmentForm
    permission_required = ('projects.add_assignment', 'projects.change_assignment', 'settings.view_member')
    template_name = "assignment/new-edit.html"

    def get_current_user(self):
        return User.objects.get(pk=self.request.user.id)
    
    def get(self, request, assignment_id=None):
        # Test GET parameters to edit or inser data
        try:
            assignment = self.model.objects.get(pk=assignment_id)
            
            ini_values = {
                'name' : assignment.name, 
                'state' : assignment.state, 
                'subject' : assignment.subject, 
                'topic' : assignment.topic, 
                'teacher' : assignment.teacher, 
                'note' : assignment.note,
             }
            
            form = self.form_class(request=request, initial=ini_values)
        except self.model.DoesNotExist:
            # Send reqest.user to the form
            assignment = None
            form = self.form_class(request=request)

        context = {'assignment' : assignment, 'form' : form}
        return render(request, self.template_name, context)

    def post(self, request, assignment_id=None):
        form = self.form_class(request.POST, request=request)
        try:
            # Prepare data to save
            assignment = self.model.objects.get(pk=assignment_id)
            
            if form.is_valid():
                assignment.name = form.cleaned_data['name']
                assignment.state = form.cleaned_data['state']
                assignment.subject = form.cleaned_data['subject']
                assignment.topic = form.cleaned_data['topic']
                assignment.author = self.get_current_user() # Select box or automatic??
                assignment.note = form.cleaned_data['note']
                assignment.save()
            return HttpResponseRedirect(reverse("projects:assignment-detail", kwargs={'assignment_id':assignment_id}))
        except self.model.DoesNotExist:
            # New data to save
            if form.is_valid():
                assignment = form.save(commit=False)
                assignment.teacher = self.get_current_user()
                assignment.save()
                form.save_m2m()            
            return HttpResponseRedirect('{}#top'.format(reverse("projects:assignment-index")))
    
    
class DetailView(PermissionRequiredMixin, TemplateView):
    """Show details of selected assignemnt with a link to edit."""
    
    model = Assignment
    permission_required = ('projects.view_assignment')
    template_name = "detail.html"

    def get(self, request, assignment_id):
        assignment = self.model.objects.get(pk=assignment_id)
        assignment_states = Assignment.States.choices
        
        context = {'assignment':assignment, 'assignment_states': assignment_states}
        return render(request, 'assignment/detail.html', context)
    