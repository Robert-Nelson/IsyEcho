__author__ = 'Robert Nelson'
__copyright__ = "Copyright (C) 2015 Robert Nelson"
__license__ = "BSD"

__all__ = ['Director', 'Light', 'ConfigApi']

from flask import Flask
from flask_oauthlib.provider import OAuth2Provider


class MyFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update({
        'extensions': ['jinja2.ext.do',  'jinja2.ext.with_'],
        'trim_blocks': True,
        'lstrip_blocks': True
    })


app = MyFlask(__package__)

app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///db.sqlite',
})

oauth = OAuth2Provider(app)

import ConfigApi
