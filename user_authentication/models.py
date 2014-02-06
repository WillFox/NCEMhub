from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User

LOCALITY_CHOICES=(
	('LBNL','Lawerence Berkeley NAtional Laboratory'),
	('NA','Not Listed'),
	#('',''),
)

#Patron is simply what we call the user and allows meta data to be attatched to a user
class Patron(models.Model):
	user				= models.OneToOneField(User)
	first_name			= models.CharField(max_length=100)
	last_name			= models.CharField(max_length=100)
	user_location		= models.CharField(max_length=254)
	date_joined			= models.DateTimeField(auto_now_add=True)
	updated_at 			= models.DateTimeField(auto_now=True)
	user_bio			= models.TextField(null=True)
	def __unicode__(self):
		return self.name
"""
Organizations or institutes:
These are official groups that have 'DataRecorders' or instrumentation

These can only be made by a ***SITE ADMIN***

class Orgs_Registered(models.Model):
	name				= models.CharField(max_length=300)
	slug 				= models.SlugField()
	org_location		= models.CharField(max_length=300)
	date_joined 		= models.DateTimeField(auto_now_add=True)
	updated_at 			= models.DateTimeField(auto_now=True)
	org_bio 			= models.TextField(null=True)
	def __unicode__(self):
		return self.name

Groups or collaborations:
These are user made groups for either collaborations or
for interdepartmental user interactions.  Simply allow groups of data
to be shared easily as opposed to sharing each data set individually

class Group(models.Model):
	name				= models.CharField(max_length=300)
	slug 				= models.SlugField()
	owners				= models.ManyToManyField(User, )
	members				= 
"""
#create user object to attatch to patron object
#def create_patron_user_callback(sender, instance, **kwargs):
#	user_authentication, new = Patron.objects.get_or_create(user=instance)
#post_save.connect(create_patron_user_callback, User)
