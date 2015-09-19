#!/usr/bin/python

__author__ = 'Robert Nelson'

from pyIsyEcho import app, Director

import logging

logging.basicConfig(level=logging.DEBUG)

app.debug = True
app.director = Director.Director(config_path=app.instance_path)
app.director.start()

app.secret_key = app.director.secret_key

app.run(host='0.0.0.0', port=42000, ssl_context=(app.instance_path + '/cert.pem', app.instance_path + '/privkey.pem'))
