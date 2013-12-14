from django.contrib.auth.models import AnonymousUser
from django.http.response import Http404
from django.shortcuts import render, redirect

from help_desk.forms import ClientIssueForm
from help_desk.models import Issue, Service, Contract


def client_only(function):
    def f(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated():
            raise Http404
        if not user.is_delegate:
            raise Http404
        delegate = user.delegate
        return function(request, delegate.client, *args, **kwargs)
        # return function(request, *args, **kwargs)
    return f


def home(request):
    return redirect(issues)


@client_only
def issues(request, client, tab):
    issues = Issue.objects.filter(client=client)
    return render(request, 'client/issues.html', {
        'tab': tab,
        'issues': issues,
    })


@client_only
def create_issue(request, client, tab):
    return render(request, 'client/create_issue.html', {
        'client_issue_form': ClientIssueForm(),
    })


@client_only
def edit_issue(request, client, tab, issue_id):
    issue = Issue.objects.get(id=int(issue_id))
    return render(request, 'client/edit_issue.html', {
        'issue': issue,
    })


# @client_only
# def create_issue(request, client, tab):
#     TODO: implement
    # return redirect(issues)


@client_only
def services(request, client, tab):
    # services = Service.objects.filter(client=client)
    return render(request, 'client/services.html', {
        'services': services,
        'tab': tab,
    })


@client_only
def contracts(request, client, tab):
    contracts = Contract.objects.filter(client=client)
    return render(request, 'client/contracts.html', {
        'contracts': contracts,
        'tab': tab,
    })


@client_only
def information(request, client, tab):
    return render(request, 'client/information.html', {
        'tab': tab,
    })
