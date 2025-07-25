from django import forms
from django.forms import ModelForm
from django.forms import widgets
from django.contrib.auth.models import User
from django.http import Http404

from .models import Member
from .models import Subject
from .models import Topic


class SubjectForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Filter lead by member roles
        # ROLE_ADMIN: see all teachers and instructors
        member = Member.objects.get(user_id=self.request.user.id)
        if member.Roles.ADMIN in member.role:
            self.fields['lead'].queryset = Member.objects.filter(role__in=[Member.Roles.INSTRUCTOR, Member.Roles.TEACHER])
        else:
            self.fields['lead'].queryset = User.objects.filter(pk=self.request.user.id)
            #NOTE: Left for reference :)
            #self.fields['lead'].queryset = User.objects.filter(pk__in=self.initial.get('lead') or self.data['lead'])
            #self.fields['lead'].widget.attrs['readonly'] = True
        
    class Meta:
        model = Subject
        fields = ['name', 'lead']


class TopicForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Filter authors by member roles
        # ROLE_ADMIN: see all teachers and instructors
        member = Member.objects.get(user_id=self.request.user.id)
        if member.Roles.ADMIN in member.role or member.Roles.TEACHER in member.role:
            self.fields['author'].queryset = Member.objects.filter(role__in=[Member.Roles.INSTRUCTOR, Member.Roles.TEACHER])
        else:
            self.fields['author'].queryset = User.objects.filter(pk=self.request.user.id)

    class Meta:
        model = Topic
        fields = ['heading', 'author', 'text']
