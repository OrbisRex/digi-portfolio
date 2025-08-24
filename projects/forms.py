from django import forms
from django.forms import ModelForm

from core.models import File
from core.forms import MultipleFileField

from settings.models import Subject
from settings.models import Topic
from settings.models import Member

from .models import Descriptor
from .models import Criterion
from .models import Assignment
from .models import Submission


class BaseProjectForm(forms.Form):
    """Base servise class for all forms."""
    
    def render_checkbox_select(self, q_data, field):
        # Load criteria and render as a checkboxes.
        items = []
        try:
            for item in q_data:
                items.append((item.id, item.name))
                
            self.fields[field].queryset = q_data
            self.fields[field].widget = forms.CheckboxSelectMultiple(choices=items)
        except:
            return False


class BaseProjectModelForm(ModelForm, BaseProjectForm):
    """Base servise class for all forms based on ModelForm."""
    pass


class DescriptorForm(BaseProjectModelForm):
    
    class Meta:
        model = Descriptor
        fields = ['name', 'description', 'type', 'author']


class CriterionForm(BaseProjectModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        q_data = Descriptor.filter_by_author(user=self.request.user)
        self.render_checkbox_select(q_data, 'descriptors')
    
    class Meta:
        model = Criterion
        fields = ['name', 'note', 'group', 'weight', 'author', 'descriptors']


class AssignmentForm(BaseProjectModelForm):
    
    # Get request from the view and select only assignments belonging to current user.
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Filter lead or author by member roles
        # ROLE_ADMIN: see all teachers and instructors
        member = Member.objects.get(user_id=self.request.user.id)
        if member.Roles.ADMIN in member.role:
            self.fields['subject'].queryset = Subject.objects.all()
            self.fields['topic'].queryset = Topic.objects.all()
        else:    
            self.fields['subject'].queryset = Subject.objects.filter(
                lead=self.request.user.id)
            self.fields['topic'].queryset = Topic.objects.filter(
                author=self.request.user.id)

        q_data = Criterion.filter_by_author(user=self.request.user)
        self.render_checkbox_select(q_data, 'criteria')

    class Meta:
        model = Assignment
        fields = ['subject', 'topic', 'name', 'note' , 'criteria', 'state']


class AddCriteriaForm(BaseProjectModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        q_data = Criterion.filter_by_author(user=self.request.user)
        self.render_checkbox_select(q_data, 'criteria')

    class Meta:
        model = Assignment
        fields = ['criteria']


class SubmissionFilesForm(forms.Form):
    name = forms.CharField(max_length=255, label='Name', required=True)
    note = forms.CharField(max_length=255, label='Note', required=True)
    path = MultipleFileField(label='Files')
    state = forms.ChoiceField(choices=File.States, label='State')
    

class SubmissionForm(BaseProjectModelForm):
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        self.fields['assignment'].queryset = Assignment.filter_by_author(user=self.request.user)
        q_data = File.filter_by_author(user=self.request.user)
        self.render_checkbox_select(q_data, 'file')

    class Meta:
        model = Submission
        fields = ['assignment', 'name', 'note', 'state', 'text', 'file']
