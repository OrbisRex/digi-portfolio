from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from settings.models import Subject
from settings.models import Topic
from settings.models import Member


class Assignment(models.Model):
    class State(models.TextChoices):
        PUBLIC = 'STATE_PUBLIC', _('Public')
        DRAFT = 'STATE_DRAFT', _('Draft')
        ARCHIVED = 'STATE_ARCHIVED', _('Archived')

    ##Fileds    
    #NOTE: Change teacher to author!
    name = models.CharField(max_length=255, null=False)
    state = models.JSONField(choices=State.choices)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.CharField(max_length=255, null=True)
    update_time = models.DateTimeField(auto_now=True)
    
    ##Metadata
    
    ##Methods    
    def __str__(self):
        return self.name
