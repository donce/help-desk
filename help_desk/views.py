# encoding=utf8
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as login_user, logout as logout_user
from django.http import Http404

from client.views import home as client_home

from models import BaseUser, Request
from forms import MODEL_FORMS


def employee_only(function):
    def f(request, *args, **kwargs):
        if not request.user.is_employee():
            raise Http404
        employee = request.user.employee
        return function(request, employee, *args, **kwargs)

    return f


def main(request):
    if request.user.is_employee():
        return redirect(management_home)
    return redirect(client_home)


def home(request):
    if request.user.is_authenticated():
        return main(request)
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login_user(request, form.get_user())
            return main(request)
        else:
            print 'invalid'
    else:
        form = AuthenticationForm()
    return render(request, 'home.html', {
        'form': form,
    })


def logout(request):
    logout_user(request)
    return redirect('/')


@employee_only
def management_home(request, employee):
    return render(request, 'management/home.html')


@employee_only
def solve_issues(request, employee):
    requests = employee.issues()
    return render(request, 'management/solve_issues.html', {
        'requests': requests,
    })


@employee_only
def manage_issues(request, employee):
    requests = Request.objects.all()

    return render(request, 'management/manage_issues.html', {
        'requests': requests,
    })


def get_form(model, instance=None):
    if model not in MODEL_FORMS:
        raise Http404
    form = MODEL_FORMS[model]
    if instance:
        modelClass = form.Meta.model
        try:
            instance = modelClass.objects.get(pk=instance)
        except modelClass.DoesNotExist:
            raise Http404
        return form(instance=instance)
    return form()


def get_model(model):
    if model not in MODEL_FORMS:
        raise Http404
    return MODEL_FORMS[model].Meta.model


@employee_only
def models(request, employee):
    model_types = [name for name in MODEL_FORMS]
    print model_types
    return render(request, 'management/models/list_all.html', {
        'models': model_types,
    })

MODEL_MANAGEMENT_FIELDS = {
    'client': [
        ('title', 'Pavadinimas'),
        ('address', 'Adresas')
    ],
    'employee': [
        ('first_name', 'Vardas'),
        ('last_name', u'Pavardė'),
        ('role', 'Pareigos'),
        ('phone_number', 'Telefonas'),
        ('email', u'El. paštas')
    ],
    'contract': [
        ('number', 'Numeris'),
        ('title', 'Pavadinimas'),
        ('client', 'Klientas'),
        ('start', 'Pradžia'),
        ('end', 'Pabaiga'),
    ],
    'service': [
        ('description', 'Aprašymas'),
        ('limit_inc', 'Incidento limitas'),
        ('limit_req', 'Paklausimo limitas')
    ]
}

@employee_only
def model_list(request, employee, model):
    objects = get_model(model).objects.all()
    fields = MODEL_MANAGEMENT_FIELDS[model] if model in MODEL_MANAGEMENT_FIELDS else []
    print fields
    return render(request, 'management/models/list_objects.html', {
        'objects': objects,
        'fields': fields,
        'model': model,
    })


@employee_only
def model_add(request, employee, model):
    form = get_form(model)
    return render(request, 'management/models/add.html', {
        'form': form,
    })


@employee_only
def model_edit(request, employee, model, instance):
    form = get_form(model, instance)
    return render(request, 'management/models/edit.html', {
        'model': model,
        'object': get_model(model).objects.get(id=instance),
        'form': form,
    })


@employee_only
def model_remove(request, employee, model, instance):
    pass

#TODO: implement
#confirmation?
