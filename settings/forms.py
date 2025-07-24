from django import forms
from django.forms import ModelForm

from .models import Member
from .models import Subject
from .models import Topic


class SubjectForm(ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'lead']


class TopicForm(ModelForm):
    class Meta:
        model = Topic
        fields = ['heading', 'author', 'text']
