from django import forms

from help_desk.models import BaseUser


class UserForm(forms.ModelForm):
    def __init__(self, _creating=False, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.creating = _creating

    class Meta:
        model = BaseUser
