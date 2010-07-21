
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from django.test.testcases import urlsplit, urlunsplit
from django.conf import settings


class ViewTest(TestCase):
    '''
    TestCase for view testing
    '''

    def setUp(self):
        self.client = Client()

    def check_url(self, url_name, status=200, kwargs=None, current_app=None):
        """check_url a URL and require a specific status code before proceeding"""
        url = reverse(url_name, kwargs=kwargs, current_app=current_app)
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, status)
        return response

    def check_login_required(self, url_name, kwargs=None, current_app=None):
        """ Check if response is a redirect to login page (ignoring GET variables) """
        url = reverse(url_name, kwargs=kwargs, current_app=current_app)
        response = self.client.get(url)

        #remove GET variables, for example '?next=..'
        scheme, netloc, path, query, fragment = urlsplit(response['Location'])
        response['Location'] = urlunsplit(('http', 'testserver', path, None, None))

        self.assertRedirects(response, getattr(settings, 'LOGIN_URL', '/accounts/login/'))
        return response
