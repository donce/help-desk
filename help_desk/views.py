# encoding=utf-8
from datetime import timedelta
from datetime import datetime

from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.http import Http404
import pytz
from common.deflection import set_deflection, get_deflection

from help_desk.administration import XLSXImporter, clean_database
from help_desk.forms import ImportForm, StatisticsForm, DeflectionForm
from help_desk.models import Deflection
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

    return render(request, 'management/solve_issues.html', {
        'fields': ISSUE_FIELDS,
        'objects': filtered_issues,
        'model': 'Issue',
        'tab': tab,
    })


def mark_issue_solved(issue):
    issue.solve()


def mark_issue_rejected(issue):
    issue.reject()


def unassign_issue(issue):
    issue.returnIssue()


def delete_issue(issue):
    #TODO: add warning message
    issue.delete()


@tab
@employee_only
def view_issue(request, employee, tab, issue):
    viewed_issue = Issue.objects.get(id=issue)

    action = get_action(request.GET, 'action', ('solve', 'reject', 'return', 'delete'))
    action_funcs = {'solve': mark_issue_solved,
                    'reject': mark_issue_rejected,
                    'return': unassign_issue,
                    'delete': delete_issue}

    if action != None:
        action_funcs[action](viewed_issue)

    if action == 'delete' or action == 'return':
        return redirect('/management/solve_issues')

    return render(request, 'management/view_issue.html', {
        'issue': viewed_issue,
        'tab': tab
    })


@tab
@employee_only
def manage_issues(request, employee, tab):
    issues = Issue.objects.all()
    filter = get_filter(request.GET, 'filter', ('all', 'keep', 'drop'))

    filteredIssues = doIssueFiltering(issues, 'assignment', filter)

    return render(request, 'management/manage_issues.html', {
        'fields': ISSUE_FIELDS,
        'issues': filteredIssues,
        'model': 'Issue',
        'tab': tab,
    })


@tab
@employee_only
def edit_issue(request, employee, tab, issue_id):
    issue = Issue.objects.get(id=issue_id)
    if issue.current == None:
        issue_form = IssueForm(employee=employee, edit=True, instance=issue, initial={'assigned_to': None})
    else:
        issue_form = IssueForm(employee=employee, edit=True, instance=issue, initial={'assigned_to': issue.current.worker})

    action = get_action(request.GET, 'action', ('delete'))
    if action != None:
        delete_issue(issue)
        return redirect('/management/manage_issues')

    #if we have already posted
    if request.method == 'POST':
        issue_form = IssueForm(employee, True, request.POST, instance=issue)
        if issue_form.is_valid():
            issue_form.save();
            return redirect('/management/manage_issues')
    return render(request, 'management/edit_issue.html', {
        'issue' : issue,
        'issue_form': issue_form,
        'tab': tab
    })


@tab
@employee_only
def create_issue(request, employee, tab):
    issue_form = IssueForm
    if request.method == 'POST':
        issue_form = IssueForm(employee, False, data=request.POST)
        if issue_form.is_valid():
            issue_form.save()
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
    return model_list(request, tab=tab)


MODEL_MANAGEMENT_FIELDS = {
    'client': [
        ('title', 'Pavadinimas'),
        ('address', 'Adresas')
    ],
    'employee': [
        ('first_name', 'Vardas'),
        ('last_name', u'Pavardė'),
        ('get_role_display', 'Pareigos'),
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
        ('title', 'Pavadinimas'),
        ('limit_inc', 'Incidento limitas'),
        ('limit_req', 'Paklausimo limitas')
    ]
}

ISSUE_FIELDS = [
    ('title', _('Name')),
    ('get_type_display', _('Type')),
    ('service', _('Service')),
        ('current', _('Assigned To')),
    ('created', _('Created On')),
    ('closed', _('Closed On')),
    ('get_status_display', _('Status'))
]


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
        form = form_class(True, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(model_list, model)
    else:
        form = form_class()
    return render(request, 'management/models/add.html', {
        'form': form,
        'model': model,
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
        form = form_class(False, data=request.POST, instance=instance)
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
        'deflection_form': DeflectionForm(initial={'deflection': get_deflection()}),
    })

@tab
@employee_only
def deflection(request, employee, tab):
    if request.method == 'POST':
        form = DeflectionForm(request.POST)
        if form.is_valid():
            deflection = form.cleaned_data['deflection']
            set_deflection(deflection)
    return redirect(administration)


@tab
@employee_only
def import_database(request, employee, tab):
    FILE_EXT_WHITELIST = ['xls','xlsx']
    print 'import'
    if request.method == 'POST':
        print 'post'
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            print 'valid'
            file = request.FILES['file']
            if len(file.name.split('.')) == 1:
                print 'red'
                return redirect(administration)
            if file.name.split('.')[-1] in FILE_EXT_WHITELIST:
                print 'ok'
                XLSXImporter().import_xlsx(file)
    return redirect(administration)


@tab
@employee_only
def wipe_database(request, employee, tab):
    clean_database()
    return redirect(administration)


#TODO: move to class
def get_deadine(issue):
    #can haz zervice?
    if issue.service == None:
        return None

    #check if we can haz deadlinez
    if issue.service.limit_inc == None and issue.type == INC:
        return None
    else:
        limit = issue.service.limit_inc

    if issue.service.limit_req == None and issue.type == REQ:
        return None
    else:
        limit = issue.service.limit_req

    return issue.created + timedelta(hours=limit)


#TODO: move to class
def is_late(issue):
    deadline = get_deadine(issue)

    #check if we even have a deadline
    if deadline == None:
        return False

    #compare deadline
    if datetime.now().replace(tzinfo=pytz.UTC) > deadline:
        return True
    return False


def get_late_issues(start, end):
    late_issues = [];
    for issue in Issue.objects.all():
        if is_late(issue) and issue.created >= start and issue.created <= end:
            late_issues.append(issue)
    return late_issues



@tab
@employee_only
def statistics(request, employee, tab):
    form = StatisticsForm(request.GET)
    start = None
    end = None
    if form.is_valid():
        start = form.cleaned_data['start']
        end = form.cleaned_data['end']

    if start != None and end != None:
        late_issues = get_late_issues(start, end)
    else:
        late_issues = []

    return render(request, 'management/statistics.html', {
        'form': form,
        'tab': tab,
        'start': start,
        'end': end,
        'model': 'Issue',
        'fields': ISSUE_FIELDS,
        'objects': late_issues
    })
