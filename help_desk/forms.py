from django import forms
from django.forms import fields

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
        exclude = ('client', 'receive_type', 'closed', 'status', 'rating',
                   'current', 'previous')
