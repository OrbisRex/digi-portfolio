from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class File(models.Model):
    '''Represents file in the system.'''
    
    class States(models.TextChoices):
        PUBLIC = 'STATE_PUBLIC', _('Public: everyone can see')
        DRAFT = 'STATE_DRAFT', _('Draft: working on it')
        ARCHIVED = 'STATE_ARCHIVED', _('Archived: stored for me')

    ## Fileds
    name = models.CharField(max_length=255, null=False)
    note = models.CharField(max_length=255, null=True)
    # path = models.TextField(max_length=1024, null=False)
    path = models.FileField(upload_to='storage/', null=True)
    meta = models.JSONField(null=True)
    state = models.JSONField(choices=States.choices)
    version = models.IntegerField(null=False) # To record possible corrections after feedback.
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_created=True)
    updated = models.DateTimeField(auto_now=True)
    
    ## Metadata
    
    ## Methods    
    def filter_by_author(user, limit=None):
        try:
            return File.objects.filter(owner__id=user.id).order_by('-updated')[:limit]
        except File.DoesNotExist:
            return None

    def __str__(self):
        return self.name
