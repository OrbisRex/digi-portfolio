from django.contrib import admin

from .models import Descriptor
from .models import Criterion
from .models import Assignment

admin.site.register(Descriptor)
admin.site.register(Criterion)
admin.site.register(Assignment)
