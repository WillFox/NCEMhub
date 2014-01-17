
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
import os, inspect
def users(request):	
	template_name = 'NCEMhub/base_home.html'
	data_path = r"../../../data"
	userlist = os.listdir(data_path)
	return render(request, template_name,{'user_list':userlist})
def microscopes(request, user_id):
	template_name = 'NCEMhub/microscope_list.html'
	data_path = r"../../../data"
	data_path = data_path + '/' + user_id
	microscope_list = os.listdir(data_path)
	return render(request, template_name , {'data_list':microscope_list})
def dates(request,user_id,microscope_id):
	template_name = 'NCEMhub/date_list.html'
	data_path = r"../../../data"
	data_path = data_path + '/' + user_id + '/' + microscope_id
	microscope_list = os.listdir(data_path)
	return render(request, template_name, {'date_list':data_list})
def home(request):
	return HttpResponseRedirect('/gallery')
