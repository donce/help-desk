from django import forms
from help_desk.models import Issue


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ('service', 'type', 'title', 'description')


class RatingForm(forms.Form):
    rating = forms.IntegerField(label='rating', min_value=0, max_value=10)