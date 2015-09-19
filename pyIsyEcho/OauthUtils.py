__author__ = 'Robert Nelson'
__copyright__ = "Copyright (C) 2014 Robert Nelson"
__license__ = "BSD"

__all__ = ['User', 'Client', 'Grant', 'Token']

from flask import session
from pyIsyEcho import app, oauth

from datetime import datetime, timedelta

import logging

logger = logging.getLogger(__package__)


class Client(object):
    def __init__(self, **kwargs):
        self.client_id = kwargs['id']
        self.client_secret = kwargs['secret']

        self._redirect_uris = "https://pitangui.amazon.com/partner-authorization/establish http://localhost:8000/authorized"
        self._default_scopes = "IsyEcho"

    @property
    def client_type(self):
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []


class Grant(object):
    def __init__(self, **kwargs):
#        self.id = kwargs['id']
        self.code = kwargs['code']

        self.redirect_uri = kwargs['redirect_uri']
        self.expires = kwargs['expires']
        self.scopes = kwargs['scopes']

    def delete(self):
        return self


class Token(object):
    def __init__(self, **kwargs):
        # currently only bearer is supported
        self.token_type = kwargs['token_type']
        self.access_token = kwargs['access_token']
        self.refresh_token = kwargs['refresh_token']
        self.expires = kwargs['expires']
        self._scopes = kwargs['scopes']

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


@oauth.clientgetter
def load_client(client_id):
    client = app.director.client
    if client is not None and client_id == client['id']:
        return Client(id=client['id'], secret=client['secret'])
    else:
        return None


@oauth.grantgetter
def load_grant(client_id, code):
    return app.director.grant


@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
    app.director.grant = Grant(code=code['code'], redirect_uri=request.redirect_uri, scopes=request.scopes,
                               expires=datetime.utcnow() + timedelta(seconds=100))

    return app.director.grant


@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    token = app.director.token
    if access_token:
        return token.access_token
    elif refresh_token:
        return token.refresh_token


@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
    expires_in = token.pop('expires_in')
    expires = datetime.utcnow() + timedelta(seconds=expires_in)

    app.director.token = Token(access_token=token['access_token'],
                               refresh_token=token['refresh_token'],
                               token_type=token['token_type'],
                               scopes=token['scope'],
                               expires=expires)


def current_user():
    if 'user' in session:
        return app.director.user
    return None
