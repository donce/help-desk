# encoding=utf-8
from datetime import timedelta
from datetime import datetime
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.util import ErrorList

from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.http import Http404
import pytz
from common.deflection import set_deflection, get_deflection


from help_desk.administration import XLSXImporter
from help_desk.forms import ImportForm, StatisticsForm, DeflectionForm
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
    sorting = get_action(request.GET, 'sort',
                         ('title', '-title',
                          'type', '-type',
                          'service', '-service',
                          'current', '-current',
                          'created', '-created',
                          'closed', '-closed',
                          'status', '-status'))
    if sorting is None:
        issues = Issue.objects.filter(current__worker=employee)
    else:
        issues = Issue.objects.filter(current__worker=employee).order_by(sorting)
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
    sorting = get_action(request.GET, 'sort',
                         ('title', '-title',
                          'type', '-type',
                          'service', '-service',
                          'current', '-current',
                          'created', '-created',
                          'closed', '-closed',
                          'status', '-status'))

    if sorting is None:
        issues = Issue.objects.all()
    else:
        issues = Issue.objects.all().order_by(sorting)
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

    #if we have already posted
    if request.method == 'POST':
        issue_form = IssueForm(employee, True, request.POST, instance=issue)
        if issue_form.is_valid():
            issue_form.save();
            return redirect('/management/manage_issues')
    return render(request, 'management/edit_issue.html', {
        'issue': issue,
        'issue_id': issue_id,
        'issue_form': issue_form,
        'tab': tab
    })

@tab
@employee_only
def delete_issue(request, employee, tab, issue_id):
    issue = Issue.objects.get(id=issue_id)
    issue.delete()
    return redirect('/management/manage_issues')

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
        ('title', _('Title'), 'title'),
        ('address', _('Address'), 'address'),
    ],
    'employee': [
        ('first_name', _('First name'), 'first_name'),
        ('last_name', _('Last name'), 'last_name'),
        ('get_role_display', _('Role'), 'role'),
        ('phone_number', _('Phone number'), 'phone_number'),
        ('email', _('Email'), 'email'),
    ],
    'contract': [
        ('number', _('Number'), 'number'),
        ('title', _('Title'), 'title'),
        ('client', _('Client'), 'client'),
        ('start', _('Start'), 'start'),
        ('end', _('End'), 'end'),
    ],
    'service': [
        ('title', _('Title'), 'title'),
        ('limit_inc', _('Incident limit'), 'limit_inc'),
        ('limit_req', _('Request limit'), 'limit_req'),
    ],
    'delegate': [
        ('client', _('Client'), 'client'),
        ('first_name', _('First name'), 'first_name'),
        ('last_name', _('Last name'), 'last_name'),
        ('phone_number', _('Phone number'), 'phone_number'),
        ('email', _('Email'), 'email'),
        ('active', _('Active'), 'active'),
    ]
}

model_items = [[name, MODEL_FORMS[name]._meta.model._meta.verbose_name] for name in MODEL_FORMS]


ISSUE_FIELDS = [
    ('title', _('Name'), 'title'),
    ('get_type_display', _('Type'), 'type'),
    ('service', _('Service'), 'service'),
    ('current', _('Assigned To'), 'current'),
    ('created', _('Created On'), 'created'),
    ('closed', _('Closed On'), 'closed'),
    ('get_status_display', _('Status'), 'status')
]


@tab
@employee_only
def model_list(request, employee, tab, model='service'):
    sorting_keys = ()
    for field in MODEL_MANAGEMENT_FIELDS[model]:
        sorting_keys = sorting_keys + (field[0], '-' + field[0])

    sorting = get_action(request.GET, 'sort', sorting_keys)

    if sorting is None:
        objects = get_model(model).objects.all()
    else:
        objects = get_model(model).objects.all().order_by(sorting)
    fields = MODEL_MANAGEMENT_FIELDS[model] if model in MODEL_MANAGEMENT_FIELDS else []
    return render(request, 'management/models/list_objects.html', {
        'objects': objects,
        'fields': fields,
        'model': model,
        'models': model_items,
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
        'models': model_items,
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
        'models': model_items,
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
def administration(request, employee, tab, form=ImportForm()):
    return render(request, 'management/administration.html', {
        'tab': tab,
        'import_form': form,
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
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            clean = form.cleaned_data['clean']
            errors = form._errors.setdefault(NON_FIELD_ERRORS, ErrorList())
            split = file.name.split('.')
            if len(split) != 1 and split[-1] in FILE_EXT_WHITELIST:
                if XLSXImporter().import_xlsx(file, clean):
                    return redirect('/')
                else:
                    errors.append(_('Error while importing file occurred.'))
            else:
                errors.append(_('Wrong file format.'))

    else:
        form = ImportForm()
    return administration(request, tab=tab, form=form)


def get_late_issues(start, end):
    late_issues = [];
    for issue in Issue.objects.all():
        if issue.is_late() and start <= issue.created <= end:
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
