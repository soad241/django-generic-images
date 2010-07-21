#coding: utf-8
from django.conf.urls.defaults import *
from django.http import Http404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.db import models
from django.db.models.query import QuerySet
from django.utils.functional import wraps

def get_site_decorator(site_param='site', obj_param='obj', context_param='context'):
    ''' It is a function that returns decorator factory useful for PluggableSite
        views. This decorator factory returns decorator that do some
        boilerplate work and make writing PluggableSite views easier.
        It passes PluggableSite instance to decorated view,
        retreives and passes object that site is attached to and passes
        common context. It also passes and all the decorator factory's
        keyword arguments.

        For example usage please check photo_albums.views.

        Btw, this decorator seems frightening for me. It feels that
        "views as PluggableSite methods" approach can easily make this decorator
        obsolete. But for now it just works.
    '''
    def site_method(**extra_params):
        def decorator(fn):
            @wraps(fn)
            def wrapper(request, **kwargs):
                try:
                    site = kwargs.pop(site_param)
                except KeyError:
                    raise ValueError("'%s' parameter must be passed to "
                                     "decorated view (%s)" % (site_param, fn))

                # Pop parameters to be passed to actual view function.
                params={}
                for key in extra_params:
                    value = kwargs.pop(key, extra_params[key])
                    params.update({key:value})

                # Now there are only site.object_getter lookup parameters in
                # kwargs. Get the object and compute common request context.
                try:
                    obj = site.object_getter(**kwargs)
                except models.ObjectDoesNotExist:
                    raise Http404("Base object does not exist.")

                context = site.get_common_context(obj)
                context_instance = RequestContext(request, context,
                                       processors=site.context_processors)

                # pass site name, the object and common request to decorated view
                params.update({
                                site_param:site,
                                obj_param: obj,
                                context_param: context_instance
                             })
                return fn(request, **params)
            return wrapper
        return decorator
    return site_method


def simple_getter(queryset, object_regex=None, lookup_field=None):
    ''' Returns simple object_getter function for use with PluggableSite.
    It takes 'queryset' with QuerySet or Model instance, 'object_regex' with
    url regex and 'lookup_field' with lookup field.
    '''
    object_regex = object_regex or r'\d+'
    lookup_field = lookup_field or 'pk'

    if isinstance(queryset, models.Model):
        qs = queryset._default_manager.all()
    elif isinstance(queryset, QuerySet) or isinstance(queryset, models.Manager):
        qs = queryset

    def object_getter(object_id):
        return qs.get(**{lookup_field: object_id})
    object_getter.regex = "(?P<object_id>%s)" % object_regex

    return object_getter


class PluggableSite(object):
    ''' Base class for reusable apps.
        The approach is similar to django AdminSite.
        For usage case please check photo_albums app.
   '''

    def __init__(self,
                 instance_name,
                 app_name,
                 queryset = None,
                 object_regex = None,
                 lookup_field = None,
                 extra_context=None,
                 template_object_name = 'object',
                 has_edit_permission = lambda request, obj: True,
                 context_processors = None,
                 object_getter = None):

        self.instance_name = instance_name
        self.extra_context = extra_context or {}
        self.app_name = app_name
        self.has_edit_permission = has_edit_permission
        self.template_object_name = template_object_name
        self.context_processors = context_processors

        if object_regex or lookup_field or (queryset is not None):
            if object_getter is not None:
                raise ValueError('It is ambiguos what lookup method should be '
                                'used: old (queryset+object_regex+lookup_field)'
                                ' or new (object_getter).')
            self.object_getter = simple_getter(queryset, object_regex, lookup_field)
        elif object_getter is not None:
            self.object_getter = object_getter
        else:
            raise ValueError('Please provide object_getter or queryset.')


    def reverse(self, url, args=None, kwargs=None):
        ''' Reverse an url taking self.app_name in account '''
        return reverse("%s:%s" % (self.instance_name, url,),
                        args=args,
                        kwargs=kwargs,
                        current_app = self.app_name)


    def check_permissions(self, request, object):
        if not self.has_edit_permission(request, object):
            raise Http404('Not allowed')


    def get_common_context(self, obj):
        context = {self.template_object_name: obj, 'current_app': self.app_name}
        if (self.extra_context):
            context.update(self.extra_context)
        return context


    def make_regex(self, url):
        '''
            Make regex string for ``PluggableSite`` urlpatterns: prepend url
            with parent object's url and app name.

            See also: http://code.djangoproject.com/ticket/11559.
        '''
        return r"^%s/%s%s$" % (self.object_getter.regex, self.app_name, url)


    def patterns(self):
        ''' This method should return url patterns (like urlpatterns variable in
            :file:`urls.py`). It is helpful to construct regex with
            :meth:`~generic_utils.app_utils.PluggableSite.make_regex` method.
            Example::

                return patterns('photo_albums.views',
                                    url(
                                        self.make_regex('/'),
                                        'show_album',
                                        {'album_site': self},
                                        name = 'show_album',
                                    ),
                               )
        '''

        raise NotImplementedError


    @property
    def urls(self):
        '''
            Use it in :file:`urls.py`.
            Example::

                urlpatterns += patterns('', url(r'^my_site/', include(my_pluggable_site.urls)),)
        '''
        return self.patterns(), self.app_name, self.instance_name
