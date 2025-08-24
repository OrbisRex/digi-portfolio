from django.contrib import admin

from .models import Descriptor
from .models import Criterion
from .models import Assignment
from .models import Submission

admin.site.register(Descriptor)
admin.site.register(Criterion)
admin.site.register(Assignment)
admin.site.register(Submission)
