import re

from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponsePermanentRedirect
from django.conf import settings


def _get_redirect_url(url_pattern_regex, redirect_pattern, requested_path):
    if url_pattern_regex.match(requested_path):
        if url_pattern_regex.match(requested_path).groups():
            return url_pattern_regex.sub(redirect_pattern, requested_path)
        else:
            return redirect_pattern


def _redirect(request, new_path):
    if request.is_secure():
        protocol = 'https'
    else:
        protocol = 'http'

    newurl = "{}://{}{}".format(
        protocol,
        request.get_host(),
        new_path
    )
    return HttpResponsePermanentRedirect(newurl)


def url_redirect_middleware(get_response):
    url_redirect_settings = getattr(settings, 'URL_REDIRECTS', None)

    if not url_redirect_settings:
        raise MiddlewareNotUsed
    else:
        URL_REDIRECTS = tuple([
            (re.compile(url_pattern), redirect_pattern)
            for url_pattern, redirect_pattern
            in url_redirect_settings
        ])

    def middleware(request):
        requested_path = request.get_full_path()

        for url_pattern_regex, redirect_pattern in URL_REDIRECTS:
            redirect_url = _get_redirect_url(
                url_pattern_regex, redirect_pattern, requested_path)

            if redirect_url:
                return _redirect(request, redirect_url)

        response = get_response(request)

        return response
    return middleware
