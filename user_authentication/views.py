from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
from user_authentication.forms import RegistrationForm,LoginForm
import os
import data_manager.urls
from user_authentication.models import Patron
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView
from data_manager import views
def PatronRegistration(request):
	if request.user.is_authenticated():
		user=request.user
		return HttpResponseRedirect(reverse('view_profile', args=[user.id]))
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
			user=User.objects.create_user(username=form.cleaned_data['username'],email = form.cleaned_data['email'], password = form.cleaned_data['password'])		
			user.save()
			# \/ \/ \/ MAKES USER FOLDER! \/  \/  \/
			#os.mkdir('../../../data/'+ user.slug[0] + '/' + user.slug)
			#patron = user.get_profile()
			#patron.name = form.cleaned_date['name']
			#patron.user_location = form.cleaned_data['user_location']
			#patron.save()
			patron = Patron(user=user, first_name=form.cleaned_data['first_name'],last_name=form.cleaned_data['last_name'], user_location=form.cleaned_data['user_location'])
			patron.save()
			return HttpResponseRedirect(reverse('view_profile', args=[user.id]))
		else:
			return render_to_response('user_authentication/register.html',{'form':form}, context_instance=RequestContext(request))
	
	else:
		''' user is not submitting the form, show them a blank registration form'''
		form = RegistrationForm()
		context = {'form':form}
		return render_to_response('user_authentication/register.html',context,context_instance=RequestContext(request))
#login required
def Profile(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('PatronLogout'))
	patron = request.user.get_profile
	user = request.user
	context = {'patron': patron, 'user':user}

	return render_to_response('user_authentication/profile.html',context,context_instance=RequestContext(request))
def EditProfile(request):
	if request.authenticated:
		return render_to_response("data_manager/main.html", dict(user=request.user,))
	else:
		return HttpResponseRedirect(reverse('data_home'))
	if request.method == 'POST':
		form = EditForm(request.POST)
		if form.is_valid():
			user=User.objects.create_user(username=form.cleaned_data['username'],email = form.cleaned_data['email'], password = form.cleaned_data['password'])		
			user.save()
			# \/ \/ \/ MAKES USER FOLDER! \/  \/  \/
			#os.mkdir('../../../data/'+ user.slug[0] + '/' + user.slug)
			#patron = user.get_profile()
			#patron.name = form.cleaned_date['name']
			#patron.user_location = form.cleaned_data['user_location']
			#patron.save()
			patron = Patron(user=user, first_name=form.cleaned_data['first_name'],last_name=form.cleaned_data['last_name'], user_location=form.cleaned_data['user_location'])
			patron.save()
			return HttpResponseRedirect(reverse('view_profile', args=[user.id]))
		else:
			return render_to_response('user_authentication/register.html',{'form':form}, context_instance=RequestContext(request))
	
	else:
		''' user is not submitting the form, show them a blank registration form'''
		form = RegistrationForm()
		context = {'form':form}
		return render_to_response('user_authentication/register.html',context,context_instance=RequestContext(request))


def LoginRequest(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect(reverse('view_profile', args=[user.id]))
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			patron = authenticate(username=username, password=password)
			if patron is not None:
				login(request,patron)
				return HttpResponseRedirect(reverse('directories'))
			else:
				return render_to_response('login.html', {'form':form}, context_instance=RquestContext(request))
		else:
			return render_to_response('login.html', {'form':form}, context_instance=RquestContext(request))
	else:
		''' user is not submitting the form, show the login form'''
		form = LoginForm()
		context = {'form': form}
		return render_to_response('user_authentication/login.html',context,context_instance=RequestContext(request))
		
def LogoutRequest(request):
	logout(request)
	return HttpResponseRedirect(reverse('data_home'))
def PatronProfile(request):
	return HttpResponseRedirect(reverse('data_home'))


