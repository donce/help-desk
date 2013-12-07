from django.utils.translation import get_language_info
from django.shortcuts import render, redirect
from help_desk.forms import ClientIssueForm


def home(request):
    return redirect(issues)


def issues(request, tab):
    return render(request, 'client/issues.html', {
        'tab': tab,
        'client_issue_form': ClientIssueForm(),
    })


def create_issue(request, tab):
    #TODO: implement
    return redirect(issues)


def services(request, tab):
    return render(request, 'client/services.html', {
        'tab': tab,
    })


def contracts(request, tab):
    return render(request, 'client/contracts.html', {
        'tab': tab,
    })


def information(request, tab):
    return render(request, 'client/information.html', {
        'tab': tab,
    })
