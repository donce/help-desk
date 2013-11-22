from django.forms import ModelForm

from models import Service, Client, Employee, Contract


class ServiceForm(ModelForm):
    class Meta:
        model = Service


class ClientForm(ModelForm):
    class Meta:
        model = Client


class EmployeeForm(ModelForm):
    class Meta:
        model = Employee


class ContractForm(ModelForm):
    class Meta:
        model = Contract


MODEL_FORMS = {
'service': ServiceForm,
'client': ClientForm,
'employee': EmployeeForm,
'contract': ContractForm,
}
