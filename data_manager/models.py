from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from string import join
from django.core.files import File
from os.path import join as pjoin
from tempfile import *
import os
import Image as PImage
from ncemhub.settings import MEDIA_ROOT, DATA_ROOT
from shutil import *
from user_authentication.models import Patron
from django.db.models import signals
#Each value unique to the data set, such as relative meta-data
class DataCharacteristic(models.Model):
    name           = models.CharField(max_length=100, unique=True)
    def __unicode__(self):
        return self.name

class Tag(models.Model):
    tag = models.CharField(max_length=50)
    def __unicode__(self):
        return self.tag

#Data recording instrument that is within the system
class DataRecorder(models.Model):
    name                = models.CharField(max_length=200)
    public              = models.BooleanField(default=False)
    slug                = models.SlugField(unique=True)
    created_on          = models.DateTimeField(auto_now_add=True)
    updated_on          = models.DateTimeField(auto_now=True)
    description         = models.TextField(max_length=4000)
    admin_owners        = models.ManyToManyField(User,related_name='user_admin_owner',null=True,blank=True)
    users               = models.ManyToManyField(User,related_name='users_data_recorder',null=True,blank=True)
    tags                = models.ManyToManyField(Tag,blank=True)
    def __unicode__(self):
        return self.name
    def tags_(self):
        lst = [x[1] for x in self.tags.values_list()]
        return str(join(lst, ', '))
    def users_(self_):
        lst = [x[1] for x in self.users.values_list()]
        return str(join(lst,', '))
    def admin_owners_(self):
        lst = [x[1] for x in self.admin_owners.values_list()]
        return str(join(lst,', '))
#Adds directory to user        
def DataRecorder_post_add(sender,action,instance,model,pk_set,reverse,signal,using,**kwargs):
    if action== 'post_add':
        temp_user=[]
        for pid in pk_set:
            temp_user.extend(model.objects.filter(id=pid))
        for tuser in temp_user:
            if not os.path.exists(DATA_ROOT+ '/'+ tuser.username[0] + '/' + tuser.username + '/' + instance.slug):
                os.mkdir(DATA_ROOT + '/' + tuser.username[0] + '/' + tuser.username + '/' + instance.slug)
    #except:
    #    pass
signals.m2m_changed.connect(DataRecorder_post_add, sender=DataRecorder.users.through)

class Repository(models.Model):
    name                = models.CharField(max_length=300)
    public              = models.BooleanField(default=False)
    created_on          = models.DateTimeField(auto_now_add=True)
    updated_on          = models.DateTimeField(auto_now=True)
    tags                = models.ManyToManyField(Tag,blank=True)
    members             = models.ManyToManyField(User,related_name='member_repository')
    owners              = models.ManyToManyField(User,related_name='owner_repository')
    def __unicode__(self):
        return self.name
    def tags_(self):
        lst = [x[1] for x in self.tags.values_list()]
        return str(join(lst, ', '))
    def members_(self):
        lst = [x[1] for x in self.members.values_list()]
        return str(join(lst, ', '))
    def owners_(self):
        lst = [x[1] for x in self.owners.values_list()]
        return str(join(lst, ', '))

class Collection(models.Model):
    name                = models.CharField(max_length=300)
    public              = models.BooleanField(default=False)
    created_on          = models.DateTimeField(auto_now_add=True)
    updated_on          = models.DateTimeField(auto_now=True)
    tags                = models.ManyToManyField(Tag,blank=True)
    members             = models.ManyToManyField(User,related_name='members_collection',null=True,blank=True)
    owners              = models.ManyToManyField(User,related_name='owners_collection',null=True, blank=True)
    data_recorder       = models.ManyToManyField(DataRecorder,null=True,blank=True)
    repositories        = models.ManyToManyField(Repository,null=True,blank=True)

    def __unicode__(self):
        return self.name
    def tags_(self):
        lst = [x[1] for x in self.tags.values_list()]
        return str(join(lst, ', '))
    def members_(self):
        lst = [x[1] for x in self.members.values_list()]
        return str(join(lst, ', '))
    def owners_(self):
        lst = [x[1] for x in self.owners.values_list()]
        return str(join(lst, ', '))
    def data_recorder_(self):
        lst = [x.data_recorder.name for x in self.data_recorder.all()]
        lst = ["<a href='/media/%s'>%s</a>" % (x, x.split('/')[-1]) for x in lst]
        return join(lst, ', ')
    def repositories_(self):
        lst = [x[1] for x in self.repositories.values_list()]
        return str(join(lst,', '))

class DataSet(models.Model):
    name                = models.CharField(max_length=300)
    public              = models.BooleanField(default=False)
    created_on          = models.DateTimeField(auto_now_add=True)
    updated_on          = models.DateTimeField(auto_now=True)
    data_original_path  = models.CharField(max_length=400)
    data_path           = models.CharField(max_length=400)#where the real data lies
                                            #metadata should be with directory path, then incorporated later
    #directory_path      = models.CharField(max_length=400)#where the data was stored 
                                            #when transferred (keep folder structure)
    #metadata_path       = models.CharField(max_length=400)
    image_rep_path      = models.CharField(max_length=400)
    description         = models.TextField(max_length=2000)
    owners              = models.ManyToManyField(User,related_name='owner_dataset')
    tags                = models.ManyToManyField(Tag,blank=True)
    data_recorder       = models.ManyToManyField(DataRecorder,blank=True)
    collections         = models.ManyToManyField(Collection, blank=True)
    data_char           = models.ManyToManyField(DataCharacteristic,through='Value', blank=True)
    
    def __unicode__(self):
        return self.name
    def owners_(self):
        lst = [x[1] for x in self.owners.values_list()]
        return str(join(lst, ', '))
    def tags_(self):
        lst = [x[1] for x in self.tags.values_list()]
        return str(join(lst, ', '))
    def data_recorder_(self):
        lst = [x[1] for x in self.data_recorder.values_list()]
        return str(join(lst, ', '))
    def collections_(self):
        lst = [x[1] for x in self.collections.values_list()]
        return str(join(lst, ', '))
    def data_char_(self):
        lst = [x[1] for x in self.data_char.values_list()]
        return str(join(lst, ', '))

class Value(models.Model):
    characteristic      = models.ForeignKey(DataCharacteristic)
    data_set            = models.ForeignKey(DataSet)
    text_value          = models.CharField(max_length=100,null=True,blank=True)
    float_value         = models.FloatField(null=True,blank=True)
    def __unicode__(self):
        return self.text_value
    def characteristic_(self):
        lst = [x[1] for x in self.characteristic.values_list()]
        return str(join(lst, ', '))
    def data_set_(self):
        lst = [x[1] for x in self.data_set.values_list()]
        return str(join(lst, ', '))

class DataCharacteristicAdmin(admin.ModelAdmin):
    list_display = ["name"]

class TagAdmin(admin.ModelAdmin):
    list_display = ["tag"]

class ValueInline(admin.TabularInline):
    model = Value
    extra = 1

class DataSetAdmin(admin.ModelAdmin):
    inlines = (ValueInline,)
    search_fields = ["name"]
    list_display = ["name","tags_","owners_","data_char_","created_on","updated_on"]
    list_filter = ["tags","owners","data_recorder","data_char"]
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

class CollectionAdmin(admin.ModelAdmin):
    search_fields = ["name","tags","members","owners"]
    list_display = ["name","tags_","members_","owners_","created_on","updated_on"]
    list_filter = ["tags","owners","members"]

class RepositoryAdmin(admin.ModelAdmin):
    search_fields = ["name","tags","members","owners"]
    list_display = ["name","tags_","members_","owners_","created_on","updated_on"]
    list_filter = ["tags","owners","members"]

class DataRecorderAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name","tags_","admin_owners_"]
    list_filter = ["tags","admin_owners"]

admin.site.register(DataCharacteristic, DataCharacteristicAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(DataSet, DataSetAdmin)
admin.site.register(Repository,RepositoryAdmin)
admin.site.register(Collection,CollectionAdmin)
admin.site.register(DataRecorder, DataRecorderAdmin)