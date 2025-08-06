from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.contrib.auth.models import User

from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView

from settings.models import Member
from settings.models import Subject
from settings.models import Topic

from .models import Descriptor
from .models import Criterion
from .models import Assignment

from .forms import DescriptorForm
from .forms import CriterionForm
from .forms import AssignmentForm
from .forms import AddCriteriaForm


class AssignmentIndexView(PermissionRequiredMixin, TemplateView):
    """Conbined view of all assignments."""

    permission_required = ('projects.view_assignment', 'settings.view_member', 'settings.view_subject')
    template_name = "index.html"
    
    def get_current_user(self):
        try:
           return User.objects.get(pk=self.request.user.id)
        except:
            return None

    def remove_wizard_steps(self, request):
        if request.session.has_key('wizard'):
            request.session.pop('wizard')

    def get(self, request, subject_id=None, topic_id=None):
        self.remove_wizard_steps(request=request) # Restart wizard steps.
        
        ## Top section #####
        try:
            if self.get_current_user().member.role == Member.Roles.ADMIN:
                assignments = Assignment.objects.all()[:8]
            else:
                assignments = Assignment.get_assignments_by_teacher(user=self.request.user, limit=8)
                
        except Assignment.DoesNotExist:
            assignments = None
        
        ## Assignments by subject section #####
        # Fetch subjects for buttons
        if self.get_current_user().member.role == Member.Roles.ADMIN:
            subjects = Subject.objects.all()
        else:
            subjects = Subject.get_subjects_by_owner(self.get_current_user())
        
        # Fetch assignments
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
        
        # Fetch assignments
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


class AssignmentNewEditView(PermissionRequiredMixin, UpdateView):
    """Creat new or edit existing assignment."""

    model = Assignment
    form_class = AssignmentForm
    permission_required = ('projects.add_assignment', 'projects.change_assignment', 'settings.view_member')
    template_name = "assignment/new-edit.html"

    def get_current_user(self):
        return User.objects.get(pk=self.request.user.id)

    def wizard_step(self, request):
        current_url = request.build_absolute_uri()
        if request.session.has_key('wizard'):
            wizard = request.session.get('wizard')
            if (current_url in wizard) and (wizard.index(current_url) < len(wizard) - 1):
                wizard.pop() # Remove last step
        else:
            wizard = []
            
        if not current_url in wizard:
            wizard.append(current_url)
            request.session.update({'wizard':wizard})
        
        return wizard[-2]
    
    def get(self, request, assignment_id=None):
        wizard = self.wizard_step(request=request)
        
        # Test GET parameters to edit or inser data
        try:
            assignment = self.model.objects.get(pk=assignment_id)
            
            ini_values = {
                'name' : assignment.name, 
                'state' : assignment.state, 
                'criteria' : [i.id for i in assignment.criteria.all()],
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

        context = {'assignment' : assignment, 'form' : form, 'wizard': wizard}
        return render(request, self.template_name, context)

    def post(self, request, assignment_id=None):
        form = self.form_class(request.POST, request=request)
        try:
            # Prepare data to save
            assignment = self.model.objects.get(pk=assignment_id)
            
            if form.is_valid():
                assignment.name = form.cleaned_data['name']
                assignment.state = form.cleaned_data['state']
                assignment.criteria.set(form.cleaned_data['criteria'])
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


class AssignmentDetailView(PermissionRequiredMixin, TemplateView):
    """Show details of selected assignemnt with a link to edit."""
    
    model = Assignment
    permission_required = ('projects.view_assignment')
    template_name = "detail.html"

    def wizard_step(self, request):
        current_url = request.build_absolute_uri()
        if request.session.has_key('wizard'):
            wizard = request.session.get('wizard')
            if (current_url in wizard) and (wizard.index(current_url) < len(wizard) - 1):
                wizard.pop() # Remove last step
        else:
            wizard = []
            
        if not current_url in wizard:
            wizard.append(current_url)
            request.session.update({'wizard':wizard})
        
        return wizard[-1]

    def get(self, request, assignment_id):
        assignment = self.model.objects.get(pk=assignment_id)
        assignment_states = Assignment.States.choices
        descriptor_types = Descriptor.Types.choices
        descriptor_weights = Criterion.Weights.choices
        request.session.update({'last_assignment_id': assignment_id}) # Save the assignment ID for use in URL
        self.wizard_step(request=request) # Set wizard steps        
        
        #print(request.get_full_path_info())
        #print(request.get_full_path())
        context = {'assignment':assignment, 'assignment_states': assignment_states, 'descriptor_types': descriptor_types}
        return render(request, 'assignment/detail.html', context)


class AssignmentAddCriteriaView(PermissionRequiredMixin, UpdateView):
    """Add criteria to an existing assignment."""

    model = Assignment
    form_class = AddCriteriaForm
    permission_required = ('projects.add_assignment', 'projects.change_assignment', 'settings.view_member')
    template_name = "assignment/add-criteria.html"

    def get_current_user(self):
        return User.objects.get(pk=self.request.user.id)

    def wizard_steps(self, request):
        current_url = request.build_absolute_uri()
        if request.session.has_key('wizard'):
            wizard = request.session.get('wizard')
            if (current_url in wizard) and (wizard.index(current_url) < len(wizard) - 1):
                wizard.pop() # Remove last step
        else:
            wizard = []

        if not current_url in wizard:
            wizard.append(current_url)
            request.session.update({'wizard':wizard})
            
        return wizard[-2]
    
    def get(self, request, assignment_id=None):
        wizard = self.wizard_steps(request=request)

        # Test GET parameters to edit or inser data
        try:
            assignment = self.model.objects.get(pk=assignment_id)
            form = self.form_class(initial={'criteria' : [i.id for i in assignment.criteria.all()]})
        except self.model.DoesNotExist:
            raise 'Create assignment first.'
        
        context = {'assignment': assignment, 'form': form, 'wizard': wizard}
        return render(request, self.template_name, context)

    def post(self, request, assignment_id=None):
        form = self.form_class(request.POST)
        try:
            # Prepare data to save
            assignment = self.model.objects.get(pk=assignment_id)
            
            if form.is_valid():
                assignment.criteria.set(form.cleaned_data['criteria'])
                assignment.save()
            return HttpResponseRedirect(reverse("projects:assignment-detail", kwargs={'assignment_id':assignment_id}, fragment="criteria"))
        except self.model.DoesNotExist:
            # New data to save
            if form.is_valid():
                assignment = form.save(commit=False)
                assignment.teacher = self.get_current_user()
                assignment.save()
                form.save_m2m()            
            return HttpResponseRedirect(reverse("projects:assignment-index", fragment="top"))
    
    
class CriterionNewEditView(PermissionRequiredMixin, UpdateView):
    """Creat new or edit existing criterion."""

    model = Criterion
    form_class = CriterionForm
    permission_required = ('projects.add_criterion', 'projects.change_criterion', 'settings.view_member')
    template_name = "assignment/criterion-new-edit.html"

    def return_page_history(self, request, return_level = 0):
        count = request.session.get('http_referer_count', 0)
        index = count - return_level
        return request.session.get('http_referer_' + str(index))

    def get_current_user(self):
        return User.objects.get(pk=self.request.user.id)

    def wizard_steps(self, request):
        current_url = request.build_absolute_uri()
        if request.session.has_key('wizard'):
            wizard = request.session.get('wizard')
            if (current_url in wizard) and (wizard.index(current_url) < len(wizard) - 1):
                wizard.pop() # Remove last step
        else:
            wizard = []

        if not current_url in wizard:
            wizard.append(current_url)
            request.session.update({'wizard':wizard})
            
        return wizard[-2]
    
    def get(self, request, criterion_id=None):
        # Fetch last page for the return button
        wizard = self.wizard_steps(request=request) # Set wizard steps
        print(wizard)
        # Test GET parameters to edit or inser data
        try:
            criterion = self.model.objects.get(pk=criterion_id)
            
            ini_values = {
                'name' : criterion.name, 
                'note' : criterion.note,
                'group' : criterion.group, 
                'weight' : criterion.weight, 
                'descriptors' : [i.id for i in criterion.descriptors.all()],
                'author' : criterion.author,
             }
            
            form = self.form_class(initial=ini_values)
        except self.model.DoesNotExist:
            # Send reqest.user to the form
            criterion = None
            form = self.form_class()

        context = {'criterion' : criterion, 'form' : form, 'wizard': wizard}
        return render(request, self.template_name, context)

    def post(self, request, criterion_id=None):
        form = self.form_class(request.POST)
        try:
            # Prepare data to save
            criterion = self.model.objects.get(pk=criterion_id)

            if form.is_valid():
                criterion.name = form.cleaned_data['name']
                criterion.note = form.cleaned_data['note']
                criterion.group = form.cleaned_data['group']
                criterion.weight = form.cleaned_data['weight']
                criterion.descriptors.set(form.cleaned_data['descriptors'])
                criterion.author = form.cleaned_data['author']
                criterion.save()
            return HttpResponseRedirect('{}#criteria'.format(reverse("projects:assignment-detail", kwargs={'assignment_id':request.session.get('last_assignment_id')})))
        except self.model.DoesNotExist:
            # New data to save
            if form.is_valid():
                criterion = form.save(commit=False)
                criterion.save()
                form.save_m2m()            
            return HttpResponseRedirect(reverse("projects:add-criteria", kwargs={'assignment_id':request.session.get('last_assignment_id')}))


class DescriptorNewEditView(PermissionRequiredMixin, UpdateView):
    """Creat new or edit existing descriptor."""

    model = Descriptor
    form_class = DescriptorForm
    permission_required = ('projects.add_descriptor', 'projects.change_descriptor', 'settings.view_member')
    template_name = "assignment/descriptor-new-edit.html"

    def return_page_history(self, request, return_level = 0):
        count = request.session.get('http_referer_count')
        index = count - return_level
        return request.session.get('http_referer_' + str(index))

    def wizard_steps(self, request):
        current_url = request.build_absolute_uri()
        if request.session.has_key('wizard'):
            wizard = request.session.get('wizard')
            if (current_url in wizard) and (wizard.index(current_url) < len(wizard) - 1):
                wizard.pop() # Remove last step
        else:
            wizard = []

        if not current_url in wizard:
            wizard.append(current_url)
            request.session.update({'wizard':wizard})
            
        return wizard[-2]

    def get(self, request, descriptor_id=None):
        # Fetch last page for the return button
        wizard = self.wizard_steps(request=request)
        last_descriptors = Descriptor.fetch_last_descriptors(user=self.request.user, limit=3)
        descriptor_types = Descriptor.Types.choices
        
        # Test GET parameters to edit or inser data
        try:
            descriptor = self.model.objects.get(pk=descriptor_id)
            
            ini_values = {
                'name' : descriptor.name, 
                'description' : descriptor.description,
                'type' : descriptor.type, 
                'author' : descriptor.author, 
             }
            
            form = self.form_class(initial=ini_values)
        except self.model.DoesNotExist:
            # Send reqest.user to the form
            descriptor = None
            form = self.form_class()

        context = {'descriptor' : descriptor, 'form' : form, 'last_descriptors': last_descriptors, 'descriptor_types': descriptor_types, 'wizard': wizard}
        return render(request, self.template_name, context)

    def post(self, request, descriptor_id=None, add_other=False):
        form = self.form_class(request.POST)
        try:
            # Prepare data to save
            descriptor = self.model.objects.get(pk=descriptor_id)
            print(request.session.get('last_assignment_id'))
            if form.is_valid():
                descriptor.name = form.cleaned_data['name']
                descriptor.description = form.cleaned_data['description']
                descriptor.type = form.cleaned_data['type']
                descriptor.author = form.cleaned_data['author']
                descriptor.save()
            return HttpResponseRedirect('{}#criteria'.format(reverse("projects:assignment-detail", kwargs={'assignment_id':request.session.get('last_assignment_id')})))
        except self.model.DoesNotExist:
            # New data to save
            if form.is_valid():
                criterion = form.save(commit=False)
                criterion.save()
                form.save_m2m()
            
            if "another" in request.POST:
                return HttpResponseRedirect(reverse("projects:descriptor-new"))
            else:
                return HttpResponseRedirect(reverse("projects:criterion-new"))
