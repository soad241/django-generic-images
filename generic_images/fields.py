#coding: utf-8
'''
django-generic-images provides fields for storing information about 
attached images count. Value is stored in model that images are 
attached to. Value is updated automatically when image is saved or deleted.
Access to this value is much faster than additional "count()" queries.
'''

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from composition.base import CompositionField
from generic_images.models import AttachedImage
from generic_images.signals import image_saved, image_deleted


def force_recalculate(obj):
    ''' Recalculate all ImageCountField and UserImageCountField fields
        in object ``obj``. 
        
        This should be used if auto-updating of these fields was disabled for
        some reason.
        
        To disable auto-update when saving AttachedImage instance 
        (for example when you need to save a lot of images and want to 
        recalculate denormalised values only after all images are saved) use 
        this pattern::
        
            image = AttachedImage(...)
            image.send_signal = False
            image.save()

    '''        
    class Stub(object):
        content_object = obj    
    img = Stub()
    image_saved.send(sender = obj.__class__, instance = img)
    
        
class ImageCountField(CompositionField):
    ''' Field with model's attached images count.
        Value of this field is updated automatically when 
        image is added or removed. Access to this field
        doesn't produce additional 'select count(*)' query,
        data is stored in table.    
        
        Example 1::

            from generic_images.fields import ImageCountField
            
            class MyModel1(models.Model):
                #... fields definitions
                image_count = ImageCountField()

        Example 2::
        
            class MyModel2(models.Model):
                #... fields definitions
                image_count = ImageCountField(native=models.IntegerField(u'MyModel2 Images count', default=0))
        
    '''
    def __init__(self, native=None):
                        
        self.internal_init(
            native = native or models.PositiveIntegerField(default=0, editable=False),
            trigger = {
                'on': (image_saved, image_deleted,),
                'do': lambda model, image, signal: AttachedImage.objects.get_for_model(model).count(),
                'field_holder_getter': lambda image: image.content_object
            }
        )


class UserImageCountField(CompositionField):
    """ Field that should be put into user's profile (AUTH_PROFILE_MODULE). 
        It will contain number of images that are attached to corresponding User.
        
        This field is useful when you want to use something like 
        :class:`~generic_images.fields.ImageCountField` for ``User`` model. 
        It is not possible to add a field to User model without 
        duck punching (monkey patching). ``UserImageCountField`` should be 
        put into user's profile (same model as defined in AUTH_PROFILE_MODULE). 
        It will contain number of images that are attached to corresponding User.
        FK attribute to User model is considered ``'user'`` by default, but this 
        can be overrided using ``user_attr`` argument to ``UserImageCountField`` 
        constructor. As with :class:`~generic_images.fields.ImageCountField`, 
        ``UserImageCountField`` constructor accepts also ``native`` argument - an 
        underlying field.
        
    """
    def __init__(self, native=None, user_attr='user'):                        
        
        def get_field_value(model, image, signal):
            return AttachedImage.objects.get_for_model(getattr(model, user_attr)).count()
        
        self.internal_init(
            native = native or models.PositiveIntegerField(default=0, editable=False),
            trigger = {
                'on': (image_saved, image_deleted,),
                'do': get_field_value,
                'field_holder_getter': lambda image: image.content_object.get_profile(),
                'sender_model': User,
            }
        )        
        
#class ImageCountField(CompositionField):
#    def __init__(self, native=None, signal=None):
#        
#        def get_field_value(model, image, signal):
##             we need to handle situation where the field with same name exists in model
##             but it is not this ImageCountField
#            if model is None:
#                return
#            ctype = ContentType.objects.get_for_model(self._composition_meta.model)
#            model_ctype = ContentType.objects.get_for_model(model)                        
#            if ctype==model_ctype:
#                try:
#                    return AttachedImage.objects.get_for_model(model).count()
#                except AttributeError:
#                    return None
#            else:
#                return 0
#                return getattr(model, self._composition_meta.name)
#        
#        self.internal_init(
#            native = native or models.PositiveIntegerField(default=0),
#            trigger = dict(
#                on = signal or (models.signals.post_save, models.signals.post_delete),
#                sender_model = AttachedImage,
#                do = get_field_value,
#                field_holder_getter = lambda image: image.content_object
#            )
#        )
#        
