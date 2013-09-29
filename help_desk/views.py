# encoding=utf8
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from models import BaseUser

def register(request):
	#TODO: implement
	print BaseUser.objects.create_client('username3', 'password', 'bendrove', 'adresas')

def main(request):
	return render(request, 'main.html', {})

def home(request):
	if request.user.is_authenticated():
		return main(request)
	if request.method == 'POST':
		form = AuthenticationForm(data=request.POST)
		if form.is_valid():
			login(request, form.get_user())
			return main(request)
		else:
			print 'invalid'
	else:
		form = AuthenticationForm()
	return render(request, 'home.html', {
		'form': form,
	})

def logout_view(request):
	logout(request)
	return redirect('/')
