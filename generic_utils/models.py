#coding: utf-8

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey

from generic_utils.managers import GenericModelManager, GenericInjector

class GenericModelBase(models.Model):
    '''
        Abstract base class for models that will be attached using
        generic relations.
        
        .. attribute:: object_id
            
            A PositiveIntegerField containing the primary key of the object the model
            is attached to.
            
        .. attribute:: content_type
        
            A ForeignKey to ContentType; this is the type of the object the model is 
            attached to.    
        
    '''

    content_type = models.ForeignKey(ContentType)
    
    object_id = models.PositiveIntegerField()
    
    content_object = GenericForeignKey()
    ''' A GenericForeignKey attribute pointing to the object the comment is
       attached to. You can use this to get at the related object
       (i.e. my_model.content_object). Since this field is a
       GenericForeignKey, it’s actually syntactic sugar on top of two underlyin
       attributes, described above.
    '''
    
    objects = GenericModelManager()
    '''
        Default manager. It is of type :class:`~generic_utils.managers.GenericModelManager`.
    '''
    
    injector = GenericInjector()
    '''
        :class:`~generic_utils.managers.GenericInjector` manager.
    '''

    class Meta:
        abstract=True
        

class TrueGenericModelBase(models.Model):
    '''
        It is similar to :class:`~generic_utils.models.GenericModelBase` but
        with TextField object_id instead of PositiveIntegerField.
    '''
    content_type = models.ForeignKey(ContentType)
    object_id = models.TextField()
    content_object = GenericForeignKey()

    objects = GenericModelManager()
    injector = GenericInjector()

    class Meta:
        abstract=True