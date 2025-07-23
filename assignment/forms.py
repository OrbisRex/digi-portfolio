from django.forms import ModelForm

from settings.models import Subject
from settings.models import Topic
from .models import Assignment


class AssignmentForm(ModelForm):
    
    # Get request from the view and select only topics belonging to current user.
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['subject'].queryset = Subject.objects.filter(
            lead=self.request.user.id)
        self.fields['topic'].queryset = Topic.objects.filter(
            author=self.request.user.id)

    class Meta:
        model = Assignment
        fields = ['subject', 'topic', 'name', 'state', 'note']
