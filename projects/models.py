from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from settings.models import Subject
from settings.models import Topic
from settings.models import Member


class Descriptor(models.Model):
    '''Descriptors for criteria.'''
    
    class Types(models.TextChoices):
        GENERAL = 'TYPE_GENERAL', _('General')
        SPECIAL = 'TYPE_SPECIAL', _('Specialised')

    ##Fileds    
    name = models.CharField(max_length=255, null=False)
    description = models.CharField(max_length=255, null=True)
    type = models.JSONField(choices=Types.choices, null=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    update_time = models.DateTimeField(auto_now=True)
    
    ##Metadata
    
    ##Methods   
    def fetch_last_descriptors(user, limit):
        return Descriptor.objects.filter(author__id=user.id).order_by('-update_time')[:limit]

    def __str__(self):
        return self.name


class Criterion(models.Model):
    '''Avaluation criteria.'''
    
    class Groups(models.TextChoices):
        GENERAL = 'GROUP_GENERAL', _('General')
        SPECIAL = 'GROUP_SPECIAL', _('Specialised')

    class Weights(models.IntegerChoices):
        LOW = 1, _('Low')
        MIDDLE = 2, _('Middle')
        HIGH = 3, _('High')

    ##Fileds    
    name = models.CharField(max_length=255, null=False)
    note = models.CharField(max_length=255, null=True)
    group = models.JSONField(choices=Groups.choices, null=False)
    weight = models.IntegerField(choices=Weights.choices, default=Weights.LOW, null=False)
    descriptors = models.ManyToManyField(Descriptor, default=Groups.GENERAL)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    update_time = models.DateTimeField(auto_now=True)
    
    ##Metadata
    
    ##Methods    
    def __str__(self):
        return self.name


class Assignment(models.Model):
    '''Assignments for students.'''
    
    class States(models.TextChoices):
        PUBLIC = 'STATE_PUBLIC', _('Public')
        DRAFT = 'STATE_DRAFT', _('Draft')
        ARCHIVED = 'STATE_ARCHIVED', _('Archived')

    ##Fileds    
    #NOTE: Change teacher to author!
    name = models.CharField(max_length=255, null=False)
    state = models.JSONField(choices=States.choices)
    criteria = models.ManyToManyField(Criterion)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.CharField(max_length=255, null=True)
    update_time = models.DateTimeField(auto_now=True)
    
    ##Metadata
    
    ##Methods    
    def get_assignments_by_teacher(user, limit):
        return Assignment.objects.filter(teacher__id=user.id).order_by('-update_time')[:limit]

    def get_assignments_by_subject(user, id):
        try:
            return Assignment.objects.filter(subject=id, teacher=user.id).order_by('-update_time')
        except:
            return None

    def get_assignments_by_topic(user, id):
        try:
            return Assignment.objects.filter(topic=id, teacher=user.id).order_by('-update_time')
        except:
            return None

    def __str__(self):
        return self.name
