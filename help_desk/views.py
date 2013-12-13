# encoding=utf-8
from django.shortcuts import render, redirect
from django.http import Http404

from help_desk.administration import XLSXImporter
from help_desk.forms import ImportForm

from models import Issue
from forms import MODEL_FORMS


def employee_only(function):
    def f(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated():
            raise Http404
        if not user.is_employee():
            raise Http404
        employee = user.employee
        return function(request, employee, *args, **kwargs)

    return f


def tab(function):
    def f(request, *args, **kwargs):
        if 'tab' in kwargs:
            tab = kwargs['tab']
            del kwargs['tab']
        else:
            tab = 'main'
        return function(request, tab, *args, **kwargs)
    return f


def get_filter(get, name, options):
    if name in get:
        value = get[name]
        if value not in options:
            value = options[0]
    else:
        value = options[0]
    return value

def doIssueFiltering(objList, filterContent, filterType):
    if filterType == 'all':
        return objList

    filteredIssues = []
    for i in objList:
        if filterContent == 'assignment':
            obj = i.current
        elif filterContent == 'status':
            obj = i.closed
        else:
            return objList

        if obj != None and filterType == 'keep':
            filteredIssues.append(i)
        elif obj == None and filterType == 'drop':
            filteredIssues.append(i)

    return filteredIssues


@tab
@employee_only
def management_home(request, employee, tab):
    return render(request, 'management/home.html', {
        'tab': tab,
    })


@tab
@employee_only
def solve_issues(request, employee, tab):
    issues = employee.issues()
    filter = get_filter(request.GET, 'filter', ('all', 'keep', 'drop'))

    filteredIssues = doIssueFiltering(issues, 'status', filter)

    return render(request, 'management/solve_issues.html', {
        'issues': filteredIssues,
        'tab': tab,
    })


@tab
@employee_only
def manage_issues(request, employee, tab):
    issues = Issue.objects.all()
    filter = get_filter(request.GET, 'filter', ('all', 'keep', 'drop'))

    filteredIssues = doIssueFiltering(issues, 'assignment', filter)

    return render(request, 'management/manage_issues.html', {
        'issues': filteredIssues,
        'tab': tab,
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


@tab
@employee_only
def models(request, employee, tab):
    model_types = [name for name in MODEL_FORMS]
    return render(request, 'management/models/list_all.html', {
        'models': model_types,
        'tab': tab,
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

@tab
@employee_only
def model_list(request, employee, tab, model):
    objects = get_model(model).objects.all()
    fields = MODEL_MANAGEMENT_FIELDS[model] if model in MODEL_MANAGEMENT_FIELDS else []
    return render(request, 'management/models/list_objects.html', {
        'objects': objects,
        'fields': fields,
        'model': model,
        'tab': tab,
    })


@tab
@employee_only
def model_add(request, employee, tab, model):
    form = get_form(model)
    return render(request, 'management/models/add.html', {
        'form': form,
        'tab': tab,
    })


@tab
@employee_only
def model_edit(request, employee, tab, model, instance):
    form = get_form(model, instance)
    return render(request, 'management/models/edit.html', {
        'model': model,
        'object': get_model(model).objects.get(id=instance),
        'form': form,
        'tab': tab,
    })


@tab
@employee_only
def model_remove(request, employee, tab, model, instance):
    m = get_model(model)
    try:
        m.objects.get(pk=instance).delete()
    except m.DoesNotExist:
        raise Http404
    return redirect(model_list, model)


@tab
@employee_only
def administration(request, employee, tab):
    return render(request, 'management/administration.html', {
        'tab': tab,
        'import_form': ImportForm(),
    })


@tab
@employee_only
def import_database(request, employee, tab):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            XLSXImporter().import_xlsx(file)
    return redirect(administration)

