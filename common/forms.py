from django import forms

from help_desk.models import BaseUser


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    def __init__(self, _creating=False, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.creating = _creating

    def clean_password(self):
        data = self.cleaned_data['password']
        if self.creating and len(data) < 8:
            raise forms.ValidationError('Ensure this value has at least 8 characters')
        elif not self.creating and 0 < len(data) < 8:
            raise forms.ValidationError('Ensure this value has at least 8 characters')
        return data

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)

        print "saving"
        if commit:
            user.username = user.email
            if len(self.cleaned_data['password']) > 0:
                user.set_password(self.cleaned_data['password'])
            user.save()
            super(UserForm, self).save()

        return user

    class Meta:
        model = BaseUser
