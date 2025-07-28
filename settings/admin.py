from django.contrib import admin

from .models import Member
from .models import Subject
from .models import Topic
from .models import Set

admin.site.register({Member, Subject, Topic, Set})
