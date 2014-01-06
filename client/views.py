from django.http.response import Http404
from django.shortcuts import render, redirect

from client.forms import IssueForm, RatingForm
# import client.forms
from common.deflection import get_time
# import help_desk.models
from help_desk.models import Issue, Contract, ISSUE_RECEIVE_TYPE_WEBSITE


def client_only(function):
    def f(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated():
            raise Http404
        if not user.is_delegate:
            raise Http404
        delegate = user.delegate
        return function(request, delegate.client, *args, **kwargs)

    return f


def home(request):
    return redirect(create_issue)


@client_only
def create_issue(request, client, tab):
    if request.method == 'POST':
        form = IssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.client = client
            issue.receive_type = ISSUE_RECEIVE_TYPE_WEBSITE
            issue.created = get_time()
            issue.save()
            return redirect(edit_issue, issue.id)
    else:
        form = IssueForm()
    issues = Issue.objects.filter(client=client)
    return render(request, 'client/issue/create.html', {
        'client_issue_form': form,
        'issues': issues,
        'tab': tab,
    })


@client_only
def edit_issue(request, client, tab, issue_id):
    issues = Issue.objects.filter(client=client)
    issue = Issue.objects.get(id=int(issue_id))
    rating_form = None
    if request.method == 'POST':
        rating_form = RatingForm(request.POST)
        if rating_form.is_valid():
            issue.rating = rating_form.cleaned_data['rating']
            issue.save()
    else:
        if issue.status == 'solved':
            rating_form = RatingForm(initial={'rating': issue.rating})
    return render(request, 'client/issue/edit.html', {
        'issue': issue,
        'issues': issues,
        'tab': tab,
        'rating_form': rating_form,
    })


@client_only
def services(request, client, tab):
    services = client.get_current_services()
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