#!/usr/bin/env python
from distutils.core import setup

setup(
      name='django-generic-images',
      version='0.36.1',
      author='Mikhail Korobov',
      author_email='kmike84@gmail.com',
      url='http://bitbucket.org/kmike/django-generic-images/',
      download_url = 'http://bitbucket.org/kmike/django-generic-images/get/tip.zip',

      description = 'Generic images pluggable django app',
      long_description = "This app provides image model (with useful managers, "
                         "methods and fields) that can be attached to any "
                         "other Django model using generic relations. "
                         "It also provides admin multi-image uploader with "
                         "client-side image resizing, animated progress bar "
                         "and before-upload image previews.\n\n"

                         "Documentation is here: http://django-generic-images.googlecode.com/hg/docs/_build/html/index.html",

      license = 'MIT license',
      packages=['generic_images', 'generic_utils'],
      package_data={'generic_images': [
                                        'locale/en/LC_MESSAGES/*',
                                        'locale/ru/LC_MESSAGES/*',
                                        'locale/pl/LC_MESSAGES/*',
                                        'templates/generic_images/*',
                                        'media/generic_images/js/*'
                                      ]},

      requires = ['django (>=1.1)'],

      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
)