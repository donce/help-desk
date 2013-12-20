from django import forms
from django.forms import fields
from common.widgets import DateWidget

from models import Service, Client, Employee, Contract, Issue


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
    class Meta:
        model = Issue
        exclude = ('created', 'closed', 'rating', 'status', 'current');


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
