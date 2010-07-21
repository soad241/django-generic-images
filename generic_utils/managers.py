
from django.db import models
from django.contrib.contenttypes.models import ContentType


def _pop_data_from_kwargs(kwargs):
    ct_field = kwargs.pop('ct_field', 'content_type')
    fk_field = kwargs.pop('fk_field', 'object_id')
    return ct_field, fk_field


class RelatedInjector(models.Manager):
    """ Manager that can emulate ``select_related`` fetching
        reverse relations using 1 additional SQL query.
    """
    def __init__(self, fk_field='object_id', *args, **kwargs):
        self.fk_field = fk_field
        super(RelatedInjector, self).__init__(*args, **kwargs)

    def inject_to(self, objects, field_name, get_inject_object = lambda obj: obj,
                  select_related = None, **kwargs):
        '''
        ``objects`` is an iterable. Related objects
            will be attached to elements of this iterable.

        ``field_name`` is the attached object attribute name

        ``get_injector_object`` is a callable that takes object in `objects`
            iterable. Related objects will be available as an attribute of the
            result of ``get_inject_object(obj)``. It is assumed that ``fk_field``
            points to  ``get_inject_object(obj)``.

        ``select_related`` is a list to be passed to select_related method for
            related objects.

        All other kwargs will be passed as arguments to queryset filter function.

        For example, we need to prefetch user profiles when we display a list of
        comments::

            # models.py
            class UserProfile(models.Model):
                user = models.ForeignKey(User, unique=True)
                info = models.CharField(max_length=100)
                objects = models.Manager()
                injector = RelatedInjector(fk_field='user')

            # views.py
            def show_comments(request, obj_id):
                ...
                comments = list(Comment.objects.for_model(obj).select_related('user'))
                UserProfile.injector.inject_to(comments, '_profile_cache',
                                               lambda comment: comment.user)

                return direct_to_template('comment_list.html', {'comments': comments})

            # in comment_list.html
            {% for comment in comments %}
                <h3>{{ comment.user }}</h3>
                <h4>{{ comment.user.get_profile.info }}</h4>
                {{ comment.comment|linebreaks }}
            {% endfor %}

        ``comment.user`` attribute will be selected using ``select_related`` and
        ``comment.user._profile_cache`` (exposed by get_profile method) will be
        selected by our injector. So there will be only 2 SQL queries for
        selecting all comments with users and user profiles.

        '''

        #get related data
        kwargs.update({self.fk_field+'__in': [ get_inject_object(obj).pk for obj in objects ]})

        data = self.get_query_set().filter(**kwargs)
        if select_related:
            data = data.select_related(select_related)

        data_dict = dict((getattr(item, self.fk_field), item) for item in list(data))

        # add info to original data
        for obj in objects:
            injected_obj = get_inject_object(obj)

            if data_dict.has_key(injected_obj):
                # fk_field was ForeignKey so there are objects in lookup dict
                get_inject_object(obj).__setattr__(field_name, data_dict[injected_obj])

            elif data_dict.has_key(injected_obj.pk):
                # fk_field was simple IntegerField so there are pk's in lookup dict
                get_inject_object(obj).__setattr__(field_name, data_dict[injected_obj.pk])


class GenericInjector(RelatedInjector):
    ''' RelatedInjector but for GenericForeignKey's.
        Manager for selecting all generic-related objects in one (two) SQL queries.
        Selection is performed for a list of objects. Resulting data is aviable as attribute
        of original model. Only one instance per object can be selected. Example usage:
        select (and make acessible as user.avatar) all avatars for a list of user when
        avatars are AttachedImage's attached to User model with is_main=True attributes.

        Example::

            from django.contrib.auth.models import User
            from generic_images.models import AttachedImage

            users = User.objects.all()[:10]
            AttachedImage.injector.inject_to(users, 'avatar', is_main=True)

            # i=0..9: users[i].avatar is AttachedImage objects with is_main=True.
            # If there is no such AttachedImage (user doesn't have an avatar),
            # users[i].avatar is None


        For this example 2 or 3 sql queries will be executed:
            1. one query for selecting 10 users,
            2. one query for selecting all avatars (images with is_main=True) for selected users
            3. and maybe one query for selecting content-type for User model

        One can reuse GenericInjector manager for other models that are supposed to
        be attached via generic relationship. It can be considered as an addition to
        GFKmanager and GFKQuerySet from djangosnippets for different use cases.

    '''

    def __init__(self, fk_field='object_id', ct_field='content_type', *args, **kwargs):
        self.ct_field = ct_field
        super(GenericInjector, self).__init__(fk_field, *args, **kwargs)


    def inject_to(self, objects, field_name, get_inject_object = lambda obj: obj, **kwargs):
        '''
        ``objects`` is an iterable. Images (or other generic-related model instances)
            will be attached to elements of this iterable.

        ``field_name`` is the attached object attribute name

        ``get_inject_object`` is a callable that takes object in `objects` iterable.
            Image will be available as an attribute of the result of
            `get_injector_object(object)`. Images attached to `get_injector_object(object)`
            will be selected.

        All other kwargs will be passed as arguments to queryset filter function.

        Example: you have a list of comments. Each comment has 'user' attribute.
        You want to fetch 10 comments and their authors with avatars. Avatars should
        be accessible as `user.avatar`::

            comments = Comment.objects.all().select_related('user')[:10]
            AttachedImage.injector.inject_to(comments, 'avatar', lambda obj: obj.user, is_main=True)

        '''

        try:
            content_type = ContentType.objects.get_for_model(get_inject_object(objects[0]))
        except IndexError:
            return objects

        kwargs.update({self.ct_field: content_type})
        return super(GenericInjector, self).inject_to(objects, field_name, get_inject_object, **kwargs)


class GenericModelManager(models.Manager):
    """ Manager with for_model method.  """

    def __init__(self, *args, **kwargs):
        self.ct_field, self.fk_field = _pop_data_from_kwargs(kwargs)
        super(GenericModelManager, self).__init__(*args, **kwargs)

    def for_model(self, model, content_type=None):
        ''' Returns all objects that are attached to given model '''
        content_type = content_type or ContentType.objects.get_for_model(model)
        kwargs = {
                    self.ct_field: content_type,
                    self.fk_field: model.pk
                 }
        objects = self.get_query_set().filter(**kwargs)
        return objects

