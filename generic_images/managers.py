from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.db.models import get_model

from generic_utils.managers import GenericModelManager


def get_model_class_by_name(name):
    app_label, model_name = name.split(".")
    model = get_model(app_label, model_name, False)
    return model


class ImagesAndUserManager(models.Manager):
    """ Useful manager for models that have AttachedImage (or subclass) field
        and 'injector=GenericIngector()' manager.        
    """
    def __init__(self, *args, **kwargs):
        try:
            image_model_class = kwargs.pop('image_model_class')
        except KeyError:
            image_model_class = 'generic_images.AttachedImage'
        self.image_model_class = get_model_class_by_name(image_model_class)
        super(ImagesAndUserManager, self).__init__(*args, **kwargs)
        
    def select_with_main_images(self, limit=None, **kwargs):
        ''' Select all objects with filters passed as kwargs.   
            For each object it's main image instance is accessible as ``object.main_image``.
            Results can be limited using ``limit`` parameter.
            Selection is performed using only 2 or 3 sql queries.            
        '''
        objects = self.get_query_set().filter(**kwargs)[:limit]
        self.image_model_class.injector.inject_to(objects,'main_image', is_main=True)
        return objects
    
    def for_user_with_main_images(self, user, limit=None):
        return self.select_with_main_images(user=user, limit=limit)
            
    def get_for_user(self, user):
        objects = self.get_query_set().filter(user=user)
        return objects
                            


class AttachedImageManager(GenericModelManager):
    ''' Manager with helpful functions for attached images
    '''
    def get_for_model(self, model):
        ''' Returns all images that are attached to given model.
            Deprecated. Use `for_model` instead.
        '''
        return self.for_model(model) 
            
    def get_main_for(self, model):
        '''
        Returns main image for given model
        '''        
        try:
            return self.for_model(model).get(is_main=True)
        except models.ObjectDoesNotExist:
            return None
            
