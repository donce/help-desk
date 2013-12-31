from django import forms
from help_desk.models import Issue


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ('service', 'type', 'title', 'description')
