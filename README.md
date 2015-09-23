# Django Url Redirect
=====================

Django's `django.contrib.redirects` app is handy, but sometimes you need a simpler system which performs
a redirect without having to lookup database records.

This is simply a piece of middleware which redirects URL requests based on regex pattern matches.


## Requirements
* Django >= 1.5

## Installation
First, install the app
`$ pip install django-url-redirect`

Then add it to your `MIDDLEWARE_CLASSES`
```python
MIDDLEWARE_CLASSES = (
    ...
    'url_redirect.middleware.UrlRedirectMiddleware',
)
```

## Configuration and Usage
You must define `URL_REDIRECTS` in your project settings.
This contains tuples in the form of: (url_pattern, redirect_pattern).
When a match for `url_pattern` is found, a redirect will be performed to the corresponding `redirect_pattern`.

e.g.
```python
URL_REDIRECTS = (
  (r'/foo/', r'/bar/'),
  ...
)
```

If `url_pattern` contains a capture group, you can use backreferences
in `redirect_pattern` to replace the captured text, e.g.
```python
URL_REDIRECTS = (
  (r'/foo/(\d+)/', r'/bar/\1/'),
  ...
)
```
