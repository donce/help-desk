from django import forms
from django.core.validators import MaxValueValidator
from django.forms import fields
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import date
from common.deflection import get_time
from common.widgets import DateWidget

from models import Service, Client, Employee, Contract, Issue, UserManager, BaseUser
from help_desk.models import Delegate


class ServiceForm(forms.ModelForm):
    def __init__(self, _creating=False, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        self.creating = _creating

    class Meta:
        model = Service


class ClientForm(forms.ModelForm):
    def __init__(self, _creating=False, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        self.creating = _creating

    class Meta:
        model = Client


class EmployeeForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    def __init__(self, _creating=False, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        self.creating = _creating

    def clean_password(self):
        data = self.cleaned_data['password']
        if self.creating and len(data) < 8:
            raise forms.ValidationError('Ensure this value has at least 8 characters')
        elif not self.creating and 0 < len(data) < 8:
            raise forms.ValidationError('Ensure this value has at least 8 characters')
        return data

    class Meta:
        model = Employee
        exclude = ('user',)

    def save(self, commit=True):
        employee = super(EmployeeForm, self).save(False)

        if self.creating:
            employee.user = BaseUser.objects.create_user(employee.email, self.cleaned_data['password'])
        elif commit:
            if len(self.cleaned_data['password']) > 0:
                employee.user.set_password(self.cleaned_data['password'])
            employee.user.username = self.cleaned_data['email']
            employee.user.save()

        if commit:
            super(EmployeeForm, self).save()
        return employee

class ContractForm(forms.ModelForm):
    def __init__(self, _creating=False, *args, **kwargs):
        super(ContractForm, self).__init__(*args, **kwargs)
        self.creating = _creating

    class Meta:
        model = Contract
        widgets = {
            'start': DateWidget,
            'end': DateWidget,
        }


class IssueForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(queryset=Employee.objects, empty_label='Unassigned', required=False)

    def __init__(self, employee=None, edit=False, *args, **kwargs):
        super(IssueForm, self).__init__(*args, **kwargs)
        self.employee = employee

        if edit:
            del self.fields['client']
            del self.fields['type']
            del self.fields['receive_type']
            del self.fields['service']

    class Meta:
        model = Issue
        exclude = ('created', 'closed', 'rating', 'status', 'current')

    def save(self, commit=True):
        issue = super(IssueForm, self).save(commit=False)
        if not issue.created:
            issue.created = get_time()
        #in case current does not exist yet
        if issue.current == None:
            if not self.cleaned_data['assigned_to'] == None:
                super(IssueForm, self).save(commit=True)
                issue.assign(self.employee, self.cleaned_data['assigned_to'])
            else:
                super(IssueForm, self).save()
                return None

        #check if we need to reassign anything
        if not issue.current.worker == self.cleaned_data['assigned_to']:
            if self.cleaned_data['assigned_to'] == None:
                issue.current = None
                issue.status = 'unassigned'
            else:
                issue.status = 'in progress'
                super(IssueForm, self).save()
                issue.assign(self.employee, self.cleaned_data['assigned_to'])

        super(IssueForm, self).save(commit=commit)


class DelegateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    def __init__(self, _creating=False, *args, **kwargs):
        super(DelegateForm, self).__init__(*args, **kwargs)
        self.creating = _creating

    def clean_password(self):
        data = self.cleaned_data['password']
        if self.creating and len(data) < 8:
            raise forms.ValidationError('Ensure this value has at least 8 characters')
        elif not self.creating and 0 < len(data) < 8:
            raise forms.ValidationError('Ensure this value has at least 8 characters')
        return data

    def save(self, commit=True):
        delegate = super(DelegateForm, self).save(commit=False)

        if self.creating:
            BaseUser.objects.create_delegate(
                delegate.client,
                delegate.email,
                self.cleaned_data['password'],
                delegate.first_name,
                delegate.last_name,
                delegate.phone_number
            )
            return delegate

        elif commit:
            delegate.user.username = delegate.email
            if len(self.cleaned_data['password']) > 0:
                delegate.user.set_password(self.cleaned_data['password'])
            delegate.user.save()
            super(DelegateForm, self).save()

        return delegate

    class Meta:
        model = Delegate
        exclude = ('user',)

MODEL_FORMS = {
    'service': ServiceForm,
    'client': ClientForm,
    'employee': EmployeeForm,
    'delegate': DelegateForm,
    'contract': ContractForm,
}


class ImportForm(forms.Form):
    file = fields.FileField(label='Failas')
    clean = fields.BooleanField(required=False, label=_('Clean database'))


class StatisticsForm(forms.Form):
    start = forms.DateTimeField(widget=DateWidget)
    end = forms.DateTimeField(widget=DateWidget)

    def is_valid(self):
        if super(StatisticsForm, self).is_valid():
            return self.cleaned_data['end'] > self.cleaned_data['start']
        return False


class DeflectionForm(forms.Form):
    deflection = fields.IntegerField(label='deflection')
