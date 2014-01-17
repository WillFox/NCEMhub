from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User

LOCALITY_CHOICES=(
	('LBNL','Lawerence Berkeley NAtional Laboratory'),
	('NA','Not Listed'),
	#('',''),
)


#Patron is simply what we call the user
class Patron(models.Model):
	user			= models.OneToOneField(User)
	name			= models.CharField(max_length=100)
	user_location		= models.CharField(max_length=254)

	def __unicode__(self):
		return self.name

"""	slug			= models.SlugField(unique=True)
	directory		= models.CharField(max_length=450)
	storage_utilized	= models.FloatField()
	storage_allocated	= models.FloatField()
	locality		= models.CharField(max_length = 200,choices = LOCALITY_CHOICES)
	micros_used		= models.ManyToManyField('directory_list.Microscope')
	bio			= models.TextField(max_length = 2000)
	date_joined		= models.DateField(auto_now_add=True)
	education		= models.CharField(max_length = 300)
	fields_experience	= models.CharField(max_length = 300)"""

#create user object to attatch to patron object
#def create_patron_user_callback(sender, instance, **kwargs):
#	user_authentication, new = Patron.objects.get_or_create(user=instance)
#post_save.connect(create_patron_user_callback, User)
