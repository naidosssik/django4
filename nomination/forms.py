from django import forms
from .models import Nominee

class NomineeForm(forms.ModelForm):
    class Meta:
        model = Nominee
        fields = [
            'nomination',
            'user',
            'project_name',
            'description',
            'contact',
            'attachment',
            'project_url',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'project_url': forms.URLInput(attrs={'placeholder': 'https://example.com'}),
        }

    def __init__(self, *args, **kwargs):
        super(NomineeForm, self).__init__(*args, **kwargs)
        self.fields['contact'].required = False
        self.fields['attachment'].required = False
        self.fields['project_url'].required = False
