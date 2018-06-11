from mock import Mock
import re

from django.test import TestCase
from django.test.utils import override_settings
from django.core.exceptions import MiddlewareNotUsed


from url_redirect.middleware import (
    url_redirect_middleware, _get_redirect_url, _redirect)


class UrlRedirectMiddlewareTests(TestCase):
    _mock_redirects = (
        (r'foo', r'bar'),
        (r'foo(.*)', r'bar\1')
    )

    def setUp(self):
        self.get_response_mock = Mock()
        self.request = Mock()

    @override_settings(URL_REDIRECTS=None)
    def test_settings_improperly_configured_raises_middlewarenotused_exception(
            self):
        with self.assertRaises(MiddlewareNotUsed):
            url_redirect_middleware(self.get_response_mock)

    @override_settings(URL_REDIRECTS=_mock_redirects)
    def test_get_redirect_url_returns_redirect_pattern_if_matched_and_no_groups_specified(self):
        url_pattern_regex = re.compile(r'/foo/')
        redirect_pattern = r'/bar/'
        requested_url = '/foo/'

        url_redirect_middleware(self.get_response_mock)

        output = _get_redirect_url(
            url_pattern_regex, redirect_pattern, requested_url)
        self.assertEqual(output, redirect_pattern)

    @override_settings(URL_REDIRECTS=_mock_redirects)
    def test_get_redirect_url_returns_correct_redirect_pattern_if_matched_and_group_specified(self):
        url_pattern_regex = re.compile(r'/foo/(\d+)/')
        redirect_pattern = r'/bar/\1/'
        requested_url = '/foo/1/'

        url_redirect_middleware(self.get_response_mock)

        output = _get_redirect_url(
            url_pattern_regex, redirect_pattern, requested_url)
        self.assertEqual(output, '/bar/1/')

    @override_settings(URL_REDIRECTS=_mock_redirects)
    def test_get_redirect_url_returns_redirect_pattern_if_matched_and_group_specified_but_no_backref(self):
        url_pattern_regex = re.compile(r'/foo/(\d+)/')
        redirect_pattern = r'/bar/'
        requested_url = '/foo/1/'

        url_redirect_middleware(self.get_response_mock)

        output = _get_redirect_url(
            url_pattern_regex, redirect_pattern, requested_url)
        self.assertEqual(output, '/bar/')

    @override_settings(URL_REDIRECTS=_mock_redirects)
    def test_redirect_returns_http_redirect_response_to_correct_url(self):
        request = Mock(**{
            'is_secure.return_value': False,
            'get_host.return_value': 'www.site.com'
        })

        url_redirect_middleware(self.get_response_mock)

        response = _redirect(request, '/foo/')
        url = response.get('location')
        self.assertEqual(url, 'http://www.site.com/foo/')
