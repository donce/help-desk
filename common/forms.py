from django import forms
from django.utils.translation import ugettext as _

from help_desk.models import BaseUser


class ProfileForm(forms.Form):
    old = forms.CharField(widget=forms.PasswordInput, label=_('Old password'))
    new = forms.CharField(widget=forms.PasswordInput, label=_('New password'))
    new2 = forms.CharField(widget=forms.PasswordInput, label=_('New password again'))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ProfileForm, self).__init__(*args, **kwargs)


    def clean(self):
        cleaned_data = super(ProfileForm, self).clean()
        if 'old' in cleaned_data and not self.user.check_password(cleaned_data['old']):
            self._errors['old'] = (_('Old password incorrect.'),)
        if 'new' in cleaned_data and 'new2' in cleaned_data and cleaned_data['new'] != cleaned_data['new2']:
            self._errors['new2'] = (_('Passwords does not match.'),)


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
