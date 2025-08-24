from django import forms
from django.forms import ModelForm

from core.models import File


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(item, initial) for item in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class FileForm(ModelForm):
    
    class Meta:
        model = File
        fields = ['name', 'note', 'path', 'state', 'version', 'owner']

