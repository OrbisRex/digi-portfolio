from django.contrib import admin

from .models import Staff
from .models import Subject
from .models import Topic
from .models import Group

admin.site.register({Staff, Subject, Topic, Group})
