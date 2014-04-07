from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from user_authentication.models import Patron
from django.views.generic.edit import UpdateView
from data_manager.models import DataSet

"""
class RegistrationForm(ModelForm):
	username		= forms.CharField(label=(u'User Name'))
	email			= forms.EmailField(label=(u'Email Address'))
	password		= forms.CharField(label=(u'Password'), widget=forms.PasswordInput(render_value=False))
	password1		= forms.CharField(label=(u'Verify Password'), widget=forms.PasswordInput(render_value=False))

	class Meta:
		model = Patron
		exclude = ('user',)
	def clean_username(self):
		username = self.cleaned_data['username']
		try:
			User.objects.get(username=username)
		except User.DoesNotExist:
			return username
		raise forms.ValidationError("That username is already taken, please select another.")

	def clean(self):
		if self.cleaned_data['password'] != self.cleaned_data['password1']:
			raise forms.ValidationError("The passwords did not match. Please try again.")
		return self.cleaned_data
class LoginForm(forms.Form):
	username	= forms.CharField(label=(u'User Name'))
	password	= forms.CharField(label=(u'Password'), widget=forms.PasswordInput(render_value=False))
"""
class DataSetForm(ModelForm):
	class Meta:
		model=DataSet
		fields= ['name']
		


class ContactForm(forms.Form):
	subject = forms.CharField(max_length=100)
	message = forms.CharField()
	message = forms.CharField()
	sender = forms.EmailField()
	cc_myself = forms.BooleanField(required=False)