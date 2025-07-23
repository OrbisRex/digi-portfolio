from django.db import models
from django.contrib.auth.models import User


class Staff(models.Model):
    TEACHER = 'ROLE_TEACHER'
    
    ACCOUNT_TYPE = {
        TEACHER: 'Teacher',
    }
    
    ##Fileds
    # NOTE: Replace by Groups - Privilage? 
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    type = models.CharField(choices=ACCOUNT_TYPE, default=TEACHER, help_text='Select an appropriate account type.')
    
    ##Metadata
    
    ##Methods
    def __str__(self):
        return self.user.username


class Subject(models.Model):
    ##Fileds
    name = models.CharField(max_length=100)
    # lead = models.ForeignKey(Staff, on_delete=models.CASCADE)
    lead = models.ManyToManyField(Staff)
    #pub_date = models.DateTimeField("date published")

    ##Metadata    
    
    ##Methods
    def __str__(self):
        return self.name


class Topic(models.Model):
    heading = models.CharField(max_length=200)
    text = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Staff, on_delete=models.CASCADE)

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
