# coding: utf-8
"""
    flask_turbolinks
    ~~~~~~~~~~~~~~~~

    Turbolinks implementation in Flask.

    :copyright: (c) 2013 by Hsiaoming Yang.
    :license: BSD, see LICENSE for more detail.
"""

try:
    from urlparse import urlparse
except ImportError:
    # python 3
    from urllib.parse import urlparse
from flask import request, session


__all__ = ('turbolinks', 'same_origin')


def turbolinks(app):
    """Enable turbolinks.

    You don't need to do any configuration, wrap your app with turbolinks::

        app = Flask(__name__)
        app.secret_key = 'secret'
        turbolinks(app)

    And everything will be ready. Put turbolinks.js in the ``<head>`` of
    your html templates, it just works.
    """

    @app.before_request
    def turbolinks_referrer():
        referrer = request.headers.get('X-XHR-Referer')
        if referrer:
            # since request.referrer is read only
            # use the misspelling referer instead
            request.referer = referrer

    @app.after_request
    def turbolinks_response(response):
        referrer = request.headers.get('X-XHR-Referer')
        if not referrer:
            # turbolinks not enabled
            return response

        method = request.cookies.get('request_method', None)
        if not method or method != request.method:
            response.set_cookie('request_method', request.method)

        if 'Location' in response.headers:
            # this is a redirect response
            loc = response.headers['Location']
            session['_turbolinks_redirect_to'] = loc

            # cross domain redirect
            if referrer and not same_origin(loc, referrer):
                response.status_code = 403
        else:
            if '_turbolinks_redirect_to' in session:
                loc = session.pop('_turbolinks_redirect_to')
                response.headers['X-XHR-Redirected-To'] = loc
        return response

    return app


def same_origin(current_uri, redirect_uri):
    parsed_uri = urlparse(current_uri)
    if not parsed_uri.scheme:
        return True
    parsed_redirect = urlparse(redirect_uri)

    if parsed_uri.scheme != parsed_redirect.scheme:
        return False

    if parsed_uri.hostname != parsed_redirect.hostname:
        return False

    if parsed_uri.port != parsed_redirect.port:
        return False
    return True
