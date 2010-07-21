from django.contrib.contenttypes.models import ContentType

def get_template_search_list(app_name, object, template_name):
    """ Returns template search list.
        Example::
        
    >>> from django.contrib.auth.models import User
    >>> user=User()
    >>> get_template_search_list('my_app', user, 'list.html')
    [u'my_app/auth/user/list.html', u'my_app/auth/list.html', 'my_app/list.html']

    """
    ctype = ContentType.objects.get_for_model(object)
    return [
        u"%s/%s/%s/%s" % (app_name, ctype.app_label, ctype.model, template_name),
        u"%s/%s/%s" % (app_name, ctype.app_label, template_name,),
        u"%s/%s" % (app_name, template_name,)
    ]

    