from django.shortcuts import render


def home(request):
    return render(request, 'client/home.html', {})


def issues(request):
    return render(request, 'client/home.html', {})


def services(request):
    return render(request, 'client/home.html', {})


def contracts(request):
    return render(request, 'client/home.html', {})


def information(request):
    return render(request, 'client/home.html', {})
