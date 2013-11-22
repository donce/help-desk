# encoding=utf8
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as login_user, logout as logout_user
from django.views.generic import ListView
from django.http import Http404

from models import BaseUser, Request, Client

from forms import MODEL_FORMS


def employee_only(function):
    def f(request, *args, **kwargs):
        if not request.user.is_employee():
            raise Http404
        employee = request.user.employee
        return function(request, employee, *args, **kwargs)

    return f


def register(request):
    #TODO: remove; add in management
    print BaseUser.objects.create_client('username3', 'password', 'bendrove', 'adresas')


def main(request):
    if request.user.is_employee():
        return redirect(management_home)
    #TODO: /self-service/ url for clients?
    return render(request, 'main.html', {})


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


@employee_only
def model_list(request, employee, model):
    objects = get_model(model).objects.all()
    path = 'management/models/list_' + model + '.html'
    print 'path:', path
    return render(request, path, {
    'objects': objects,
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
    'form': form,
    })


@employee_only
def model_remove(request, employee, model, instance):
    pass

#TODO: implement
#confirmation?
