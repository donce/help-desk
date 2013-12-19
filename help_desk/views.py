# encoding=utf-8
from django.shortcuts import render, redirect
from django.http import Http404

from help_desk.administration import XLSXImporter
from help_desk.forms import ImportForm

from models import Issue
from forms import MODEL_FORMS, IssueForm


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

def get_action(get, name, options):
    if name in get:
        value = get[name]
        if value not in options:
            return None
        return value
    else:
        return None

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
    filtered_issues = doIssueFiltering(issues, 'status', filter)
    fields = [
        ('title', 'Pavadinimas'),
        ('type', 'Tipas'),
        ('service', 'Paslauga'),
        ('assigned_to', 'Paskirta'),
        ('created', 'Sukurta'),
        ('closed', 'Pabaigta'),
        ('status', 'Statusas')
    ]

    return render(request, 'management/solve_issues.html', {
        'fields': fields,
        'objects': filtered_issues,
        'model': 'Issue',
        'tab': tab,
    })

def mark_issue_solved(issue):
    if issue.status == 'solved':
        issue.unsolve()
    else:
        issue.solve()

def mark_issue_rejected(issue):
    if issue.status == 'rejected':
        issue.unreject();
    else:
        issue.reject()

def unassign_issue(issue):
    issue.returnIssue()

def delete_issue(issue):
    #TODO: add warning message
    issue.delete()

@tab
@employee_only
def view_issue(request, employee, tab, issue):
    viewedIssue = Issue.objects.get(id = issue)

    action = get_action(request.GET, 'action', ('solve', 'reject', 'return', 'delete'))
    action_funcs = {'solve' : mark_issue_solved,
                    'reject' : mark_issue_rejected,
                    'return' : unassign_issue,
                    'delete'  : delete_issue}

    if action != None:
        action_funcs[action](viewedIssue)

    if action == 'delete' or action == 'return':
        return redirect('/management/solve_issues')

    return render(request, 'management/view_issue.html', {
        'issue': viewedIssue,
        'tab': tab
    })


@tab
@employee_only
def manage_issues(request, employee, tab):
    issues = Issue.objects.all()
    filter = get_filter(request.GET, 'filter', ('all', 'keep', 'drop'))

    filteredIssues = doIssueFiltering(issues, 'assignment', filter)

    fields = [
        ('title', 'Pavadinimas'),
        ('type', 'Tipas'),
        ('service', 'Paslauga'),
        ('assigned_to', 'Priskirta'),
        ('created', 'Sukurta'),
        ('closed', 'Pabaigta'),
        ('status', 'Statusas')
    ]


    return render(request, 'management/manage_issues.html', {
        'fields': fields,
        'issues': filteredIssues,
        'model' : 'Issue',
        'tab': tab,
    })


@tab
@employee_only
def edit_issue(request, employee, tab, issue_id):
    issue = Issue.objects.get(id=issue_id)
    issue_form = IssueForm(instance=issue)

    action = get_action(request.GET, 'action', ('delete'))
    if action != None:
        delete_issue(issue)
        return redirect('/management/manage_issues')

    #if we have already posted
    if request.method == 'POST':
        issue_form = IssueForm(request.POST, instance=issue)
        if issue_form.is_valid():

            #check for status setting
            issue = issue_form.save(commit=False)
            if issue.assigned_to == None:
                issue.status = 'unassigned'
            elif issue.status == 'unassigned':
                issue.status = 'in progress'

            #check if assignment is needed
            if not Issue.objects.get(id=issue_id).assigned_to == issue.assigned_to:
                issue.assign(employee, issue.assigned_to)

            #save
            issue.save();
            return redirect('/management/manage_issues')
    return render(request, 'management/edit_issue.html', {
        'issueForm' : issue_form,
        'tab' : tab
    })

@tab
@employee_only
def create_issue(request, employee, tab):
    issue_form = IssueForm
    if request.method == 'POST':
        issue_form = IssueForm(data=request.POST)
        if issue_form.is_valid():
            issue = issue_form.save(commit=False)
            if issue.assigned_to == None:
                issue.status = 'unassigned'
            else:
                issue.status = 'in progress'
                issue.assign(employee, issue.assigned_to)
            issue.save()
            return redirect('/management/manage_issues')
    return render(request, 'management/create_issue.html', {
        'issue_form': issue_form,
        'models': IssueForm,
        'tab': tab,
    })

def get_form(model):
    if model not in MODEL_FORMS:
        raise Http404
    form = MODEL_FORMS[model]
    return form


def get_model(model):
    if model not in MODEL_FORMS:
        raise Http404
    return MODEL_FORMS[model].Meta.model


@tab
@employee_only
def models(request, employee, tab):
    return model_list(request)


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
def model_list(request, employee, tab, model='service'):
    objects = get_model(model).objects.all()
    fields = MODEL_MANAGEMENT_FIELDS[model] if model in MODEL_MANAGEMENT_FIELDS else []
    return render(request, 'management/models/list_objects.html', {
        'objects': objects,
        'fields': fields,
        'model': model,
        'models': [name for name in MODEL_FORMS],
        'tab': tab,
    })


@tab
@employee_only
def model_add(request, employee, tab, model):
    form_class = get_form(model)
    if request.method == 'POST':
        form = form_class(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(model_list, model)
    else:
        form = form_class()
    return render(request, 'management/models/add.html', {
        'form': form,
        'models': [name for name in MODEL_FORMS],
        'tab': tab,
    })


@tab
@employee_only
def model_edit(request, employee, tab, model, instance_id):
    form_class = get_form(model)
    model_class = form_class.Meta.model
    try:
        instance = model_class.objects.get(id=instance_id)
    except model_class.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(model_list, model)
    else:
        form = form_class(instance=instance)
    return render(request, 'management/models/edit.html', {
        'model': model,
        'object': get_model(model).objects.get(id=instance_id),
        'form': form,
        'models': [name for name in MODEL_FORMS],
        'tab': tab,
    })


@tab
@employee_only
def model_remove(request, employee, tab, model, instance_id):
    m = get_model(model)
    try:
        m.objects.get(pk=instance_id).delete()
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
