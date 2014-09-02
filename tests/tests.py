from mock import Mock
import re

from django.test import TestCase
from django.test.utils import override_settings
from url_redirect.middleware import UrlRedirectMiddleware
from django.core.exceptions import MiddlewareNotUsed


class UrlRedirectMiddlewareTests(TestCase):
    _mock_redirects = (
        (r'foo', r'bar'),
        (r'foo(.*)', r'bar\1')
    )

    def setUp(self):
        self.request = Mock()

    @override_settings(URL_REDIRECTS=None)
    def test_settings_improperly_configured_raises_middlewarenotused_exception(self):
        with self.assertRaises(MiddlewareNotUsed):
            UrlRedirectMiddleware()

    @override_settings(URL_REDIRECTS=_mock_redirects)
    def test_init_copies_compiled_url_patterns_and_redirect_patterns_onto_object(self):
        middleware = UrlRedirectMiddleware()
        url_pattern_regexes, redirect_patterns = zip(*middleware.URL_REDIRECTS)

        for url_pattern, redirect_pattern in self._mock_redirects:
            self.assertIn(re.compile(url_pattern), url_pattern_regexes)
            self.assertIn(redirect_pattern, redirect_patterns)

    @override_settings(URL_REDIRECTS=_mock_redirects)
    def test_get_redirect_url_returns_redirect_pattern_if_matched_and_no_groups_specified(self):
        url_pattern_regex = re.compile(r'/foo/')
        redirect_pattern = r'/bar/'
        requested_url = '/foo/'

        middleware = UrlRedirectMiddleware()
        output = middleware._get_redirect_url(url_pattern_regex, redirect_pattern, requested_url)
        self.assertEqual(output, redirect_pattern)

    @override_settings(URL_REDIRECTS=_mock_redirects)
    def test_get_redirect_url_returns_correct_redirect_pattern_if_matched_and_group_specified(self):
        url_pattern_regex = re.compile(r'/foo/(\d+)/')
        redirect_pattern = r'/bar/\1/'
        requested_url = '/foo/1/'

        middleware = UrlRedirectMiddleware()
        output = middleware._get_redirect_url(url_pattern_regex, redirect_pattern, requested_url)
        self.assertEqual(output, '/bar/1/')

    @override_settings(URL_REDIRECTS=_mock_redirects)
    def test_get_redirect_url_returns_redirect_pattern_if_matched_and_group_specified_but_no_backref(self):
        url_pattern_regex = re.compile(r'/foo/(\d+)/')
        redirect_pattern = r'/bar/'
        requested_url = '/foo/1/'

        middleware = UrlRedirectMiddleware()
        output = middleware._get_redirect_url(url_pattern_regex, redirect_pattern, requested_url)
        self.assertEqual(output, '/bar/')

    @override_settings(URL_REDIRECTS=_mock_redirects)
    def test_redirect_returns_http_redirect_response_to_correct_url(self):
        request = Mock(**{
            'is_secure.return_value': False,
            'get_host.return_value': 'www.site.com'
        })

        middleware = UrlRedirectMiddleware()
        response = middleware._redirect(request, '/foo/')
        url = response.get('location')
        self.assertEqual(url, 'http://www.site.com/foo/')
