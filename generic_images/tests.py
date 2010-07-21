#coding: utf-8
from django.test import TestCase
from django.db import models
from generic_images.models import AttachedImage

class DumbModel(models.Model):
    pass

#class ImageOrderTest(TestCase):
#    def setUp(self):
#        self.model1 = DumbModel.objects.create()
#        self.model2 = DumbModel.objects.create()
#
#        self.image1 = AttachedImage.objects.create()