from django.conf import settings

'''
Example::
    THUMBNAIL_TYPES = {
                        'photo': "421x1000",
                        'photo_small': "130x130",
                        'avatar': '191x1000',
                      }

'''
THUMB_TYPES = getattr(settings,'THUMBNAIL_TYPES', {})

def thumbnail_types(request):
    '''
    A context processor to add possible thumbnail sizes to the current Context.
    Useful for managing possible sorl.thumbnails thumbnail's sizes
    '''
    return {'thumbs': THUMB_TYPES}