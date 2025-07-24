from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Member(models.Model):

    class Roles(models.TextChoices):
        STUDENT = 'ROLE_STUDENT', _('Student')
        INSTRUCTOR = 'ROLE_INSTRUCTOR', _('Instructor')
        TEACHER = 'ROLE_TEACHER', _('Teacher')
        ADMIN = 'ROLE_ADMIN', _('Admin')
    
    ##Fileds
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.JSONField(choices=Roles.choices, help_text='Select an appropriate role.')
    
    ##Metadata
    
    ##Methods
    def __str__(self):
        return self.user.username


class Subject(models.Model):
    ##Fileds
    name = models.CharField(max_length=100)
    # lead = models.ForeignKey(Member, on_delete=models.CASCADE)
    lead = models.ManyToManyField(Member)
    #pub_date = models.DateTimeField("date published")

    ##Metadata    
    
    ##Methods
    def __str__(self):
        return self.name


class Topic(models.Model):
    heading = models.CharField(max_length=200)
    text = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Member, on_delete=models.CASCADE)

    ##Metadata
    
    ##Methods
    def __str__(self):
        return self.heading


class Group(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    
    ##Metadata

    ##Methods
    def __str__(self):
        return self.name
