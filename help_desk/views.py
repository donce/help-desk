# encoding=utf8
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as login_user, logout as logout_user
from models import BaseUser, Request

#TODO: decorator employee_only


def register(request):
	#TODO: implement
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


def management_home(request):
	return render(request, 'management/home.html')

def solve_issues(request):
	return render(request, 'management/solve_issues.html')

def manage_issues(request):
	requests = Request.objects.all()
	
	return render(request, 'management/manage_issues.html', {
		'requests': requests,
	})

