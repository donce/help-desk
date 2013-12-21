from django import forms
from django.forms import fields
from common.widgets import DateWidget

from models import Service, Client, Employee, Contract, Issue
from django.forms import ModelChoiceField

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract


class IssueForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(queryset=Employee.objects, empty_label='Unassigned', required=False)

    def __init__(self, employee=None, *args, **kwargs):
        super(IssueForm, self).__init__(*args, **kwargs)
        self.employee = employee

    class Meta:
        model = Issue
        exclude = ('created', 'closed', 'rating', 'status', 'current');

    def save(self, commit=True):
        issue = super(IssueForm, self).save(commit=False)

        #in case current does not exist yet
        if issue.current == None:
            if not self.cleaned_data['assigned_to'] == None:
                super(IssueForm, self).save(commit=True)
                issue.assign(self.employee, self.cleaned_data['assigned_to'])
            else:
                return None

        #check if we need to reassign anything
        if not issue.current.worker == self.cleaned_data['assigned_to']:
            if self.cleaned_data['assigned_to'] == None:
                issue.current = None
            else:
                super(IssueForm, self).save(commit=True)
                issue.assign(self.employee, self.cleaned_data['assigned_to'])

        return super(IssueForm, self).save(commit=commit)


MODEL_FORMS = {
    'service': ServiceForm,
    'client': ClientForm,
    'employee': EmployeeForm,
    'contract': ContractForm,
}


class ImportForm(forms.Form):
    file = fields.FileField(label='Failas')


class ClientIssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ('service', 'type', 'title', 'description')


class StatisticsForm(forms.Form):
    start = forms.DateTimeField(widget=DateWidget)
    end = forms.DateTimeField(widget=DateWidget)

    def is_valid(self):
        if super(StatisticsForm, self).is_valid():
            return self.cleaned_data['end'] > self.cleaned_data['start']
        return False
