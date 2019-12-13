from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm

'''
NAME

        register

SYNOPSIS

        register(request)

			Parameters:
				request --> takes in an http request object
					request.POST --> data filled out by user
			Decorators:
				None

DESCRIPTION

		if form is filled out, takes in the form data passed to it and creates a new user, redirects to the login page.
		if form has no data, renders the registration page with the empty form

RETURNS
			
		return redirect('login') or render(request, 'users/register.html', {'form': form})
		redirect('login') --> sends user to the login page
		render(request, 'users/register.html', {'form': form}) --> 


AUTHOR

        Sean O'Neill
'''
def register(request):
	if request.method =='POST':
		form = UserRegisterForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			messages.success(request, f'Account created for {username}!, you can now login.')
			return redirect('login')

	else:
		form = UserRegisterForm()
	return render(request, 'users/register.html', {'form': form})