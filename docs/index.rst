.. django-generic-images documentation master file, created by
   sphinx-quickstart on Fri Sep 18 02:13:39 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=====================================
django-generic-images's documentation
=====================================

django-generic-images is a generic images pluggable django app.

This app provides image model (useful managers, methods and fields)
that can be attached to any other Django model using generic relations.
It also provides admin multi-image uploader (based on
`GearsUploader <http://bitbucket.org/kmike/gearsuploader/>`_ ) with client-side
image resizing, animated progress bar and before-upload image previews.

Requirements: django 1.1 (or trunk).

`django-composition <http://bitbucket.org/daevaorn/django-composition/>`_ is
required if you want to use
:class:`~generic_images.fields.ImageCountField` or
:class:`~generic_images.fields.UserImageCountField`.

There is an image gallery app
(`django-photo-albums <http://bitbucket.org/kmike/django-photo-albums/>`_)
based on django-generic-images.

.. toctree::
   :maxdepth: 2

   upgrade


************
Installation
************
::

    $ pip install django-generic-images

or::

    $ easy_install django-generic-images

or::

    $ hg clone http://bitbucket.org/kmike/django-generic-images/
    $ cd django-generic-images
    $ python setup.py install

Then add 'generic_images' to your ``INSTALLED_APPS`` in settings.py and run ::

    $ manage.py syncdb

If you want ``ImageCountField`` and ``UserImageCountField`` then follow
installation instructions at  http://bitbucket.org/daevaorn/django-composition/
to install django-composition.

For admin uploader to work ``generic_images`` folder from
``generic_images/media/`` should be copied to project's ``MEDIA_ROOT``.


*****
Usage
*****

Generic Images
==============

The idea is to provide an infrastructure for images that can be attached
to any django model using generic relations.

Models
------

.. autoclass:: generic_images.models.AttachedImage

.. autoclass:: generic_images.models.AbstractAttachedImage
    :show-inheritance:
    :members:

.. autoclass:: generic_images.models.BaseImageModel
    :members:


.. autoclass:: generic_images.models.ReplaceOldImageModel
    :show-inheritance:
    :members:

Admin
-----

.. automodule:: generic_images.admin
    :members:


Managers
--------

.. automodule:: generic_images.managers

.. autoclass:: generic_images.managers.AttachedImageManager
    :show-inheritance:
    :exclude-members: get_for_model
    :members:

.. autoclass:: generic_images.managers.ImagesAndUserManager
    :members:

Forms
-----

.. automodule:: generic_images.forms

.. autoclass:: generic_images.forms.AttachedImageForm()
    :show-inheritance:


Fields for denormalisation
--------------------------

.. automodule:: generic_images.fields
    :members:


Context processors
------------------

.. automodule:: generic_images.context_processors
    :members:


Generic Utils
=============


Pluggable app utils
-------------------
.. automodule:: generic_utils.app_utils
    :members:
    :undoc-members:


Models
------

.. autoclass:: generic_utils.models.GenericModelBase
    :members:

.. autoclass:: generic_utils.models.TrueGenericModelBase


Generic relation helpers
------------------------

.. automodule:: generic_utils.managers
    :members:
    :undoc-members:



Template tag helpers
--------------------

.. automodule:: generic_utils.templatetags
    :members:
    :undoc-members:


Test helpers
------------

.. automodule:: generic_utils.test_helpers
    :members:
