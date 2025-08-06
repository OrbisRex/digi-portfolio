from django.forms import ModelForm

from settings.models import Subject
from settings.models import Topic
from settings.models import Member

from .models import Descriptor
from .models import Criterion
from .models import Assignment


class DescriptorForm(ModelForm):
    
    class Meta:
        model = Descriptor
        fields = ['name', 'description', 'type', 'author']


class CriterionForm(ModelForm):
    
    class Meta:
        model = Criterion
        fields = ['name', 'note', 'group', 'weight', 'author', 'descriptors']


class AssignmentForm(ModelForm):
    
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

    class Meta:
        model = Assignment
        fields = ['subject', 'topic', 'name', 'state', 'criteria', 'note']


class AddCriteriaForm(ModelForm):
    
    class Meta:
        model = Assignment
        fields = ['criteria']
