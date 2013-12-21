from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.shortcuts import redirect, render
from django.utils.translation import check_for_language
from django import http
from django.utils.http import is_safe_url
from django.contrib.auth import login as login_user, logout as logout_user

from client.views import home as client_home
from help_desk.models import ROLE_ENGINEER, ROLE_MANAGER
from help_desk.views import management_home as employee_home, solve_issues, manage_issues


def main(request):
    if request.user.is_employee():
        role = request.user.employee.role
        if role == ROLE_MANAGER:
            redirect(manage_issues)
        elif role == ROLE_ENGINEER:
            return redirect(solve_issues)
        return redirect(employee_home)
    return redirect(client_home)


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
    return render(request, 'common/login.html', {
        'form': form,
    })


def logout(request):
    logout_user(request)
    return redirect('/')


def tab(function):
    def f(request, *args, **kwargs):
        if 'tab' in kwargs:
            tab = kwargs['tab']
            del kwargs['tab']
        else:
            tab = 'main'
        return function(request, tab, *args, **kwargs)

    return f


def set_language(request):
    next = request.REQUEST.get('next')
    if not is_safe_url(url=next, host=request.get_host()):
        next = request.META.get('HTTP_REFERER')
        if not is_safe_url(url=next, host=request.get_host()):
            next = '/'
    response = http.HttpResponseRedirect(next)
    lang_code = request.GET.get('language', None)
    print 'language', lang_code
    if lang_code and check_for_language(lang_code):
        if hasattr(request, 'session'):
            request.session['django_language'] = lang_code
        else:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
    return response
