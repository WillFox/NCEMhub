
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
import os, inspect
def home(request):
	return HttpResponseRedirect('/data/manager')
