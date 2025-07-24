from django.db import models
from django.contrib.auth.models import User

from settings.models import Subject
from settings.models import Topic
from settings.models import Member


class Assignment(models.Model):
    PUBLIC = 'Public'
    
    STATE_TYPE = {
        PUBLIC: 'Public',
    }
    
    ##Fileds    
    #NOTE: Change teacher to author!
    name = models.CharField(max_length=255, null=False)
    state = models.CharField(choices=STATE_TYPE, default=PUBLIC)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Member, on_delete=models.CASCADE)
    note = models.CharField(max_length=255, null=True)
    update_time = models.DateTimeField(auto_now=True)
    
    ##Metadata
    
    ##Methods    
    def __str__(self):
        return self.name
