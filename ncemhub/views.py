
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.shortcuts import render
from ncemhub.settings import MEDIA_URL, DATA_ROOT, MEDIA_ROOT
fro mdjango.core.urlresolvers import reverse
import os, inspect
def home(request):
	return HttpResponseRedirect(reverse('data_home'))

def about(request):
	return render_to_response("ncemhub/about.html", dict(user=request.user,
        media_url=MEDIA_URL))

def contact(request):
	return render_to_response("ncemhub/contact.html", dict(user=request.user,
        media_url=MEDIA_URL))