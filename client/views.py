from django.shortcuts import render, redirect


def home(request):
    return redirect(issues)


def issues(request, tab):
    return render(request, 'client/issues.html', {
        'tab': tab,
    })


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
