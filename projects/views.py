from django.views.generic import TemplateView
from django.template import loader

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django import forms

from core.models import File
from core.forms import FileForm

from settings.models import Member
from settings.models import Subject
from settings.models import Topic

from .models import Descriptor
from .models import Criterion
from .models import Assignment
from .models import Submission

from .forms import DescriptorForm
from .forms import CriterionForm
from .forms import AssignmentForm
from .forms import AddCriteriaForm
from .forms import SubmissionFilesForm
from .forms import SubmissionForm

class BaseView(PermissionRequiredMixin):
    """Base Assignment View to inherit common members."""
    
    def get_current_user(self):
        return get_object_or_404(User, pk=self.request.user.id)

    def return_page_history(self, request, return_level = 0):
        """Get visited URL under the return_level."""
        
        count = request.session.get('http_referer_count')
        index = count - return_level
        return request.session.get('http_referer_' + str(index))

    def create_wizard_steps(self, request, step):
        """Use a session to persist URLs of visited forms in chained editing."""
        
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
            
        return wizard[step]


class AssignmentIndexView(BaseView, TemplateView):
    """Conbined view of all assignments."""

    model = Assignment
    permission_required = ('projects.view_assignment', 'settings.view_member', 'settings.view_subject')
    template_name = 'index.html'
    
    def get(self, request, subject_id=None, topic_id=None):
        self.create_wizard_steps(request=request, step=-1)
        
        ## Top section #####
        try:
            if self.get_current_user().member.role == Member.Roles.ADMIN:
                assignments = self.model.objects.all()[:8]
            else:
                assignments = self.model.filter_by_author(user=self.request.user, limit=8)
                
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
                assignments_by_subject = self.model.objects.filter(subject=subject_id)
            else:
                assignments_by_subject = self.model.filter_by_subject(user=self.request.user, id=subject_id)
        except Subject.DoesNotExist:
            selected_subject = None
            if self.get_current_user().member.role == Member.Roles.ADMIN:
                assignments_by_subject = self.model.objects.all()[:8]
            else:
                assignments_by_subject = self.model.filter_by_author(self.get_current_user(), limit=8)
                
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
                assignments_by_topic = self.model.objects.filter(topic=topic_id)
            else:
                assignments_by_topic = self.model.filter_by_topic(user=self.request.user, id=topic_id)
        except Topic.DoesNotExist:
            selected_topic = None
            if self.get_current_user().member.role == Member.Roles.ADMIN:
                assignments_by_topic = self.model.objects.all()[:8]
            else:
                assignments_by_topic = self.model.filter_by_author(user=self.request.user, limit=8)

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


class AssignmentNewEditView(BaseView, TemplateView):
    """Creat new or edit existing assignment."""
    
    model = Assignment
    form_class = AssignmentForm
    permission_required = ('projects.add_assignment', 'projects.change_assignment', 'settings.view_member')
    template_name = 'assignment/new-edit.html'

    def get(self, request, assignment_id=None):
        wizard = self.create_wizard_steps(request=request, step=-2)
        
        # Test GET parameters to edit or inser data
        try:
            assignment = self.model.objects.get(pk=assignment_id)
            
            ini_values = {
                'name' : assignment.name, 
                'state' : assignment.state, 
                'criteria' : [i.id for i in assignment.criteria.all()],
                'subject' : assignment.subject, 
                'topic' : assignment.topic, 
                'author' : assignment.author, 
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
            return HttpResponseRedirect(reverse('projects:assignment-detail', kwargs={'assignment_id':assignment_id}))
        except self.model.DoesNotExist:
            # New data to save
            if form.is_valid():
                assignment = form.save(commit=False)
                assignment.author = self.get_current_user()
                assignment.save()
                form.save_m2m()            
            return HttpResponseRedirect(reverse('projects:assignment-index', fragment='#top'))


class AssignmentDetailView(BaseView, TemplateView):
    """Show details of selected assignemnt with a link to edit."""
    
    model = Assignment
    permission_required = ('projects.view_assignment')
    template_name = 'detail.html'

    def get(self, request, assignment_id):
        assignment = self.model.objects.get(pk=assignment_id)
        assignment_states = self.model.States.choices
        descriptor_types = Descriptor.Types.choices
        # descriptor_weights = Criterion.Weights.choices
        request.session.update({'last_assignment_id': assignment_id}) # Save the assignment ID for later use in URL (Criterion)
        self.create_wizard_steps(request=request, step=-1)
        
        context = {'assignment':assignment, 'assignment_states': assignment_states, 'descriptor_types': descriptor_types}
        return render(request, 'assignment/detail.html', context)


class AssignmentAddCriteriaView(BaseView, TemplateView):
    """Add criteria to an existing assignment."""

    model = Assignment
    form_class = AddCriteriaForm
    permission_required = ('projects.add_assignment', 'projects.change_assignment', 'settings.view_member')
    template_name = 'assignment/add-criteria.html'

    def get(self, request, assignment_id=None):
        wizard = self.create_wizard_steps(request=request, step=-2)

        # Test GET parameters to edit or inser data
        try:
            assignment = self.model.objects.get(pk=assignment_id)
            form = self.form_class(initial={'criteria' : [i.id for i in assignment.criteria.all()]})
        except self.model.DoesNotExist:
            raise 'Create an assignment first.'
        
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
            return HttpResponseRedirect(reverse('projects:assignment-detail', kwargs={'assignment_id':assignment_id}, fragment='criteria'))
        except self.model.DoesNotExist:
            # New data to save
            if form.is_valid():
                assignment = form.save(commit=False)
                assignment.author = self.get_current_user()
                assignment.save()
                form.save_m2m()            
            return HttpResponseRedirect(reverse('projects:assignment-index', fragment='top'))
    
    
class CriterionNewEditView(BaseView, TemplateView):
    """Creat new or edit existing criterion."""

    model = Criterion
    form_class = CriterionForm
    permission_required = ('projects.add_criterion', 'projects.change_criterion', 'settings.view_member')
    template_name = 'assignment/criterion-new-edit.html'

    def get(self, request, criterion_id=None):
        # Fetch the last page for the return button
        wizard = self.create_wizard_steps(request=request, step=-2) # Set wizard steps

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
            return HttpResponseRedirect(reverse('projects:assignment-detail', kwargs={'assignment_id':request.session.get('last_assignment_id')}, fragment='#criteria'))
        except self.model.DoesNotExist:
            # New data to save
            if form.is_valid():
                criterion = form.save(commit=False)
                criterion.save()
                form.save_m2m()            
            return HttpResponseRedirect(reverse('projects:add-criteria', kwargs={'assignment_id':request.session.get('last_assignment_id')}))


class DescriptorNewEditView(BaseView, TemplateView):
    """Creat new or edit existing descriptor."""

    model = Descriptor
    form_class = DescriptorForm
    permission_required = ('projects.add_descriptor', 'projects.change_descriptor', 'settings.view_member')
    template_name = 'assignment/descriptor-new-edit.html'

    def get(self, request, descriptor_id=None):
        # Fetch the last page for the return button
        wizard = self.create_wizard_steps(request=request, step=-2)
        last_descriptors = self.model.filter_last(user=self.request.user, limit=3)
        descriptor_types = self.model.Types.choices
        
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

    def post(self, request, descriptor_id=None):
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
            return HttpResponseRedirect(reverse('projects:assignment-detail', kwargs={'assignment_id':request.session.get('last_assignment_id')}, fragment='#criteria'))
        except self.model.DoesNotExist:
            # New data to save
            if form.is_valid():
                descriptor = form.save(commit=False)
                descriptor.save()
                form.save_m2m()
            
            # Branching for Save and Save and Add another
            if "another" in request.POST:
                return HttpResponseRedirect(reverse('projects:descriptor-new'))
            else:
                return HttpResponseRedirect(reverse('projects:criterion-new'))


class SubmissionIndexView(BaseView, TemplateView):
    """Conbined view of all available submissions."""

    model = Submission
    permission_required = ('projects.view_submission', 'projects.view_assignment', 'settings.view_subject', 'settings.view_topic', 'settings.view_member')
    template_name = 'submission-index.html'
    
    def get(self, request, subject_id=None, topic_id=None, admission_id=None):
        self.create_wizard_steps(request=request, step=-1)
        
        ## Top section #####
        try:
            if self.get_current_user().member.role == Member.Roles.ADMIN:
                submissions = self.model.objects.all()[:8]
            else:
                submissions = self.model.filter_by_author(Submission, user=self.request.user, limit=8)
        except self.model.DoesNotExist:
            submissions = None
        
        ## Section: Submissions by subject #####
        # Fetch subjects for buttons
        if self.get_current_user().member.role == Member.Roles.ADMIN:
            subjects = Subject.objects.all()
        else:
            subjects = Subject.get_subjects_by_owner(self.get_current_user())
        
        # Fetch submissions
        try:
            selected_subject = Subject.objects.get(pk = subject_id)
            if self.get_current_user().member.role == Member.Roles.ADMIN:
                submissions_by_subject = self.model.objects.filter(assignment__subject=subject_id)
            else:
                submissions_by_subject = self.model.filter_by_subject(user=self.request.user, id=subject_id, limit=8)
        except Subject.DoesNotExist:
            selected_subject = None
            if self.get_current_user().member.role == Member.Roles.ADMIN:
                submissions_by_subject = self.model.objects.all()[:8]
            else:
                submissions_by_subject = self.model.filter_by_author(Submission, self.get_current_user(), limit=8)
                
        ## Section: Assignments by topic #####
        # List of topics for buttons
        if self.get_current_user().member.role == Member.Roles.ADMIN:
            topics = Topic.objects.all()
        else:
            topics = Topic.get_topics_by_owner(self.request.user)
        
        # Fetch submissions
        try:
            selected_topic = Topic.objects.get(pk = topic_id)
            if self.get_current_user().member.role == Member.Roles.ADMIN:
                submissions_by_topic = self.model.objects.filter(assignment__topic=topic_id)
            else:
                submissions_by_topic = self.model.filter_by_topic(user=self.request.user, id=topic_id)
        except Topic.DoesNotExist:
            selected_topic = None
            if self.get_current_user().member.role == Member.Roles.ADMIN:
                submissions_by_topic = self.model.objects.all()[:8]
            else:
                submissions_by_topic = self.model.filter_by_author(Submission, user=self.request.user, limit=8)

        # Render all data
        context = {'submissions':submissions, 
                   'subjects':subjects, 
                   'topics':topics, 
                   'selected_subject':selected_subject, 
                   'submissions_by_subject':submissions_by_subject, 
                   'selected_topic':selected_topic, 
                   'submissions_by_topic':submissions_by_topic
                   }
        return render(request, 'assignment/submission-index.html', context)


class SubmissionDetailView(BaseView, TemplateView):
    pass


class SubmissionNewFilesView(BaseView, TemplateView):
    """Upload new files for a submission."""

    model = File
    form_class = SubmissionFilesForm
    permission_required = ('projects.add_file')
    template_name = 'assignment/submission-files-upload.html'
    
    def form_valid(self, form):
        files = form.clean_data['path']
        
        #TODO: Validations: type (jpg, png, gif, pdf, text files), size        
        for file in files:
            pass
        return super().form_valid(form)
    
    def get(self, request):
        # Fetch the last page for the return button
        wizard = self.create_wizard_steps(request=request, step=-1)
        file_states = self.model.States.choices
        form = self.form_class()

        context = {'form' : form, 'file_states': file_states, 'wizard': wizard}
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('path')
            for file in files:
                new_file = File(path=file)
                new_file.name = form.cleaned_data['name']
                new_file.note = form.cleaned_data['note']
                new_file.state = form.cleaned_data['state']
                new_file.version = 1
                new_file.owner = self.get_current_user()
                new_file.created = timezone.now()
                new_file.save()
            
            return HttpResponseRedirect(reverse('projects:submission-new'))
        else:
            form = self.form_class(request.POST, request.FILES)
            context = {'form' : form}
        return render(request, self.template_name, context)


class SubmissionNewEditView(BaseView, TemplateView):
    """Creat new or edit existing submission."""

    model = Submission
    form_class = SubmissionForm
    permission_required = ('projects.add_submission', 'projects.change_submission', 'settings.view_member')
    template_name = 'assignment/submission-new-edit.html'

    def get(self, request, submission_id=None):
        # Fetch the last page for the return button
        wizard = self.create_wizard_steps(request=request, step=-2)
        submission_states = self.model.States.choices
        
        # Test GET parameters to edit or inser data
        try:
            submission = self.model.objects.get(pk=submission_id)
            
            ini_values = {
                'name' : submission.name, 
                'note' : submission.note,
                'text' : submission.text, 
                'file' : [ i.id for i in submission.file.all()], 
                'state' : submission.state, 
                'assignment' : submission.assignment,
                'author' : submission.author, 
             }
            
            form = self.form_class(request=request, initial=ini_values)
        except self.model.DoesNotExist:
            # Send reqest.user to the form
            submission = None
            form = self.form_class(request=request)

        context = {'submission' : submission, 'form' : form, 'submission_states': submission_states, 'wizard': wizard}
        return render(request, self.template_name, context)

    def post(self, request, submission_id=None):
        form = self.form_class(request.POST, request=request)
        try:
            # Prepare data to save
            submission = self.model.objects.get(pk=submission_id)
            if form.is_valid():
                submission.assignment = form.cleaned_data['assignment']
                submission.name = form.cleaned_data['name']
                submission.note = form.cleaned_data['note']
                submission.state = form.cleaned_data['state']
                submission.text = form.cleaned_data['text']
                submission.file.set(form.cleaned_data['file'])
                submission.author = self.get_current_user()
                submission.update_time = timezone.now()
                submission.save()
            return HttpResponseRedirect(reverse('projects:submission-detail', kwargs={'submission_id':submission_id}))
        except self.model.DoesNotExist:
            # New data to save
            #ass = request.POST.get('assignment')
            #ids = request.POST.getlist('file')
            #id_list = []
            #for id in ids:
            #    id_list.append((id, id))
            #form.fields['file'].choices = id_list
            #print(id_list)
            if form.is_valid():
                submission = form.save(commit=False)
                submission.author = self.get_current_user()
                submission.create_time = timezone.now()
                submission.save()
                form.save_m2m()
                return HttpResponseRedirect(reverse('projects:submission-index'))
            else:
                form = self.form_class(request.POST, request=request)
                context = {'form' : form}
                return render(request, self.template_name, context)