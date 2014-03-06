from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.db.models import signals
from ncemhub.settings import DATA_ROOT
import os
LOCALITY_CHOICES=(
	('LBNL','Lawerence Berkeley National Laboratory'),
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
		return unicode(self.user)

"""
The following creates a folder for the newly created user in the designated file system
"""
"""Argument explanation:

       sender - The model class. (MyModel)
       instance - The actual instance being saved.
       created - Boolean; True if a new record was created.

       *args, **kwargs - Capture the unneeded `raw` and `using`(1.3) arguments.
"""
def Patron_post_save(sender,instance,created,*args,**kwargs):
    if created:
    	if not os.path.exists(DATA_ROOT+ '/'+ instance.user.username):
			os.mkdir(DATA_ROOT+ '/' + instance.user.username)

post_save.connect(Patron_post_save, sender=Patron)


#create user object to attatch to patron object
#def create_patron_user_callback(sender, instance, **kwargs):
#	user_authentication, new = Patron.objects.get_or_create(user=instance)
#post_save.connect(create_patron_user_callback, User)
