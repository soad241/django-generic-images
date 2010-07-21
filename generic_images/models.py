#coding: utf-8
import os
#import random

from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.db.models import Max
from django.utils.translation import ugettext_lazy as _

from generic_images.signals import image_saved, image_deleted
from generic_images.managers import AttachedImageManager
from generic_utils.models import GenericModelBase


class BaseImageModel(models.Model):
    ''' Simple abstract Model class with image field.

        .. attribute:: image

            ``models.ImageField``
    '''

    def get_upload_path(self, filename):
        ''' Override this to customize upload path '''
        raise NotImplementedError

    def _upload_path_wrapper(self, filename):
        return self.get_upload_path(filename)

    image = models.ImageField(_('Image'), upload_to=_upload_path_wrapper)

    class Meta:
        abstract = True



class ReplaceOldImageModel(BaseImageModel):
    '''
        Abstract Model class with image field.
        If the file for image is re-uploaded, old file is deleted.
    '''

    def _replace_old_image(self):
        ''' Override this in subclass if you don't want
            image replacing or want to customize image replacing
        '''
        try:
            old_obj = self.__class__.objects.get(pk=self.pk)
            if old_obj.image.path != self.image.path:
                path = old_obj.image.path
                default_storage.delete(path)
        except self.__class__.DoesNotExist:
            pass

    def save(self, *args, **kwargs):
        if self.pk:
            self._replace_old_image()
        super(ReplaceOldImageModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True



class AbstractAttachedImage(ReplaceOldImageModel, GenericModelBase):
    '''
        Abstract Image model that can be attached to any other Django model
        using generic relations.

        .. attribute:: is_main

            BooleanField. Whether the image is the main image for object.
            This field is set to False automatically for all images attached to
            same object if image with is_main=True is saved to ensure that there
            is only 1 main image for object.

        .. attribute:: order

            IntegerField to support ordered image sets.
            On creation it is set to max(id)+1.

    '''


    user = models.ForeignKey(User, blank=True, null=True,
                             verbose_name=_('User'))
    '''A ForeignKey to associated user, for example user who uploaded image.
    Can be empty.'''

    caption = models.TextField(_('Caption'), null=True, blank=True)
    'TextField caption for image'

    is_main = models.BooleanField(_('Main image'), default=False)

    order = models.IntegerField(_('Order'), default=0)

    objects = AttachedImageManager()
    '''Default manager of :class:`~generic_images.managers.AttachedImageManager`
    type.'''

    def next(self):
        ''' Returns next image for same content_object and None if image is
        the last. '''
        try:
            return self.__class__.objects.for_model(self.content_object,
                                                    self.content_type).\
                            filter(order__lt=self.order).order_by('-order')[0]
        except IndexError:
            return None

    def previous(self):
        ''' Returns previous image for same content_object and None if image
        is the first. '''
        try:
            return self.__class__.objects.for_model(self.content_object,
                                                    self.content_type).\
                            filter(order__gt=self.order).order_by('order')[0]
        except IndexError:
            return None

    def get_order_in_album(self, reversed_ordering=True):
        ''' Returns image order number. It is calculated as (number+1) of images
        attached to the same content_object whose order is greater
        (if 'reverse_ordering' is True) or lesser (if 'reverse_ordering' is
        False) than image's order.
        '''
        lookup = 'order__gt' if reversed_ordering else 'order__lt'
        return self.__class__.objects.\
                        for_model(self.content_object, self.content_type).\
                        filter(**{lookup: self.order}).count() + 1


    def _get_next_pk(self):
        max_pk = self.__class__.objects.aggregate(m=Max('pk'))['m'] or 0
        return max_pk+1


#    def put_as_last(self):
#        """ Sets order to max(order)+1 for self.content_object
#        """
#        last = self.__class__.objects.exclude(id=self.id).\
#                        filter(
#                           object_id = self.object_id,
#                           content_type = self.content_type,
#                        ).aggregate(max_order=Max('order'))['max_order'] or 0
#        self.order = last+1


    def get_file_name(self, filename):
        ''' Returns file name (without path and extenstion)
            for uploaded image. Default is 'max(pk)+1'.
            Override this in subclass or assign another functions per-instance
            if you want different file names (ex: random string).
        '''
#        alphabet = "1234567890abcdefghijklmnopqrstuvwxyz"
#        # 1e25 variants
#        return ''.join([random.choice(alphabet) for i in xrange(16)])

        # anyway _get_next_pk is needed for setting `order` field
        return str(self._get_next_pk())


    def get_upload_path(self, filename):
        ''' Override this in proxy subclass to customize upload path.
            Default upload path is
            :file:`/media/images/<user.id>/<filename>.<ext>`
            or :file:`/media/images/common/<filename>.<ext>` if user is not set.

            ``<filename>`` is returned by
            :meth:`~generic_images.models.AbstractAttachedImage.get_file_name`
            method. By default it is probable id of new image (it is
            predicted as it is unknown at this stage).
        '''
        user_folder = str(self.user.pk) if self.user else 'common'

        root, ext = os.path.splitext(filename)
        return os.path.join('media', 'images', user_folder,
                            self.get_file_name(filename) + ext)


    def save(self, *args, **kwargs):
        send_signal = getattr(self, 'send_signal', True)
        if self.is_main:
            related_images = self.__class__.objects.filter(
                                                content_type=self.content_type,
                                                object_id=self.object_id
                                            )
            related_images.update(is_main=False)

        if not self.pk: # object is created
            if not self.order: # order is not set
                self.order = self._get_next_pk() # let it be max(pk)+1

        super(AbstractAttachedImage, self).save(*args, **kwargs)

        if send_signal:
            image_saved.send(sender = self.content_type.model_class(),
                             instance = self)


    def delete(self, *args, **kwargs):
        send_signal = getattr(self, 'send_signal', True)
        super(AbstractAttachedImage, self).delete(*args, **kwargs)
        if send_signal:
            image_deleted.send(sender = self.content_type.model_class(),
                               instance = self)


    def __unicode__(self):
        try:
            if self.user:
                return u"AttachedImage #%d for [%s] by [%s]" % (
                         self.pk, self.content_object, self.user)
            else:
                return u"AttachedImage #%d for [%s]" % (
                        self.pk, self.content_object,)
        except:
            try:
                return u"AttachedImage #%d" % (self.pk)
            except TypeError:
                return u"new AttachedImage"

    class Meta:
        abstract=True



class AttachedImage(AbstractAttachedImage):
    '''
        Image model that can be attached to any other Django model using
        generic relations. It is simply non-abstract subclass of
        :class:`~generic_images.models.AbstractAttachedImage`
    '''
    class Meta:
        ordering = ['-order']
