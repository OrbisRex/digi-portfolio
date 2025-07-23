from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.template import loader

from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView

from .models import Staff
from .models import Assignment
from .models import Subject

from .forms import AssignmentForm


class IndexView(PermissionRequiredMixin, TemplateView):
    """Conbined view of all assignments."""

    permission_required = ('assignment.view_assignment', 'settings.view_staff', 'settings.view_subject')
    template_name = "index.html"
    
    def get_current_user(self):
        return Staff.objects.get(pk=self.request.user.id)
        
    def get_queryset(self):
        return Assignment.objects.filter(teacher__id=self.request.user.id).order_by('-update_time')[:8]
    
    def get(self, request, subject_id=None):
        print(self.get_permission_required())   
        print(request.user.has_perm('assignment.edit_assignment'))   

        ## Top section
        try:
            assignments = self.get_queryset()
        except Assignment.DoesNotExist:
            assignments = None
        
        ## Assignments by subject section
        # List of subjects for buttons
        subjects = Subject.objects.all().order_by('name')
        
        # Select assignments
        try:
            selected_subject = Subject.objects.get(pk = subject_id)
            assignments_by_subject = Assignment.objects.filter(subject=subject_id, teacher=self.get_current_user()).order_by('-update_time')
        except Subject.DoesNotExist:
            selected_subject = None
            assignments_by_subject = self.get_queryset()

        # Render all data
        context = {'assignments':assignments, 'subjects':subjects, 'selected_subject':selected_subject, 'assignments_by_subject':assignments_by_subject}
        return render(request, 'assignment/index.html', context)


class NewEditView(PermissionRequiredMixin, UpdateView):
    """Creat new or edit existing assignment."""

    model = Assignment
    form_class = AssignmentForm
    permission_required = ('assignment.add_assignment', 'assignment.change_assignment', 'settings.view_staff')
    template_name = "assignment/new-edit.html"

    def get_current_user(self):
        return Staff.objects.get(pk=self.request.user.id)
    
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
            return HttpResponseRedirect(reverse("assignment:detail", kwargs={'assignment_id':assignment_id}))
        except self.model.DoesNotExist:
            # New data to save
            if form.is_valid():
                assignment = form.save(commit=False)
                assignment.teacher = self.get_current_user()
                assignment.save()
                form.save_m2m()            
            return HttpResponseRedirect('{}#top'.format(reverse("assignment:index")))
    
    
class DetailView(PermissionRequiredMixin, TemplateView):
    """Show details of selected assignemnt with a link to edit."""
    
    model = Assignment
    permission_required = ('assignment.view_assignment')
    template_name = "detail.html"

    def get(self, request, assignment_id):
        assignment = self.model.objects.get(pk=assignment_id)

        context = {'assignment':assignment}
        return render(request, 'assignment/detail.html', context)
    