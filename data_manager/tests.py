"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from data_manager.models import Tag, DataRecorder, Repository, Collection, DataSet
from django.contrib.auth.models import User
from django.test.client import Client
from django.core.urlresolvers import reverse


from django.test import TestCase

def create_data_set(name, public, created_on, updated_on, 
	data_path, image_rep_path, description, owners, tags, 
	data_recorder,collections):
	return DataSet.objects.create()

def create_repository(name,public,created_on,updated_on, tags,
	members,owners):
	return Repository.objects.create()

def create_collection(name, public, created_on, updated_on, 
	tags, members, owners, data_recorder, repositories):
	return Collection.objects.create()

def create_data_recorder(name,public,slu,created_on,
	updated_on,description,admin_owners,users,tags):
	return DataRecorder.objects.create()

def create_tag(tag):
	return Tag.objects.create()



class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
class AuthenticationTest(TestCase):
	tag1 		= create_tag('carbon')
	tag1repeat	= create_tag('carbon')
	tag2		= create_tag('nanotube')
	

	def test_views_public(self):

		self.assertEqual(1 + 1, 2)