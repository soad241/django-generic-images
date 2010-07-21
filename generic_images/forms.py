#coding: utf-8
from django import forms

from generic_images.models import AttachedImage

class AttachedImageForm(forms.ModelForm):
    ''' Simple form for AttachedImage model with ``image`` and ``caption`` fields.'''

    class Meta:
        model = AttachedImage
        fields = ['image', 'caption']
