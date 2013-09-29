# encoding=utf8
from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout

def main(request):
	return render(request, 'main.html', {})

def home(request):
	if request.user.is_authenticated():
		return main(request)
	else:
		print 'not auth'
	print request.method
	if request.method == 'POST':
		print 'post'
		form = AuthenticationForm(data=request.POST)
		print request.POST
		if form.is_valid():
			#username = request.POST['username']
			#password = request.POST['password']
			#user = authenticate(username=username, password=password)
			login(request, form.get_user())
			return main(request)
	else:
		form = AuthenticationForm()
	return render(request, 'home.html', {
		'form': form,
	})

def logout_view(request):
	logout(request)
	return redirect('/')
