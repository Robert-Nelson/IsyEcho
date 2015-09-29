__author__ = 'Robert Nelson'
__copyright__ = "Copyright (C) 2014 Robert Nelson"
__license__ = "BSD"

from pyIsyEcho import app
from functools import wraps
from flask import g, flash, jsonify, request, redirect, render_template, session, url_for

import re
import logging


logger = logging.getLogger(__package__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    if app.director.settings_complete:
        return redirect(url_for('show_lights'), code=302)
    else:
        return redirect(url_for('show_settings'), code=302)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


@app.route('/settings', methods=['GET', 'POST'])
def show_settings():
    if request.method == "POST":
        settings = parse_settings(request.values)
        app.director.update_settings(settings)
        flash("Settings updated")
        app.director.save_config()
        return redirect(url_for('show_settings'), code=303)
    else:
        if not app.director.settings_complete:
            disable_nav = 'disabled'
        else:
            disable_nav = ''
        return render_template('settings.html', settings=app.director.settings, disable_nav=disable_nav)


def parse_settings(values):
    settings = {
        'IsyIP': values['IsyIP'], 'IsyUser': values['IsyUser'], 'IsyPass': values['IsyPass'],
        'EchoUser': values['EchoUser'], 'EchoPass': values['EchoPass'],
    }
    return settings


@app.route('/show_lights', methods=['GET', 'POST'])
def show_lights():
    if app.director.isy_controller is None:
        flash("ISY settings must be saved first", category="error")
        return redirect(url_for('show_settings'), code=302)
    if request.method == "POST":
        lights = parse_lights(request.values)
        flash("Lights saved")
        app.director.update_lights(lights)
        app.director.save_config()
        return redirect(url_for('show_lights'), code=303)
    else:
        sorted_keys = map(lambda x: x[0], sorted(app.director.lights.items(), key=lambda x: x[1].name))
        return render_template('lights.html', lights=app.director.lights, sorted_keys=sorted_keys)


def parse_lights(values):
    re_light = re.compile(r'lights\[(\d+)\]\[(\w+)\]')

    lights = {}

    for value in values:
        m = re_light.match(value)
        if m is not None and m.lastindex == 2:
            array_index = int(m.group(1))
            if array_index not in lights:
                lights[array_index] = {}
            lights[array_index][m.group(2)] = values[value]

    return lights


@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == app.director.echo_user and password == app.director.echo_password:
            session['user'] = username
            return redirect(request.referrer)
        return redirect('/login')
    #user = current_user()
    #return render_template('login.html', user=user)


@app.route('/request', methods=['POST'])
def handle_request():
    logger.debug("Request: " + request.data)
    namespace = request.json['header']['namespace']
    operation = request.json['header']['name']
    response = generate_error_response(request.json, "UNSUPPORTED_OPERATION", "Unsupported name - " + operation + " in namespace " + namespace)
    if namespace == 'Discovery':
        if operation == 'DiscoverAppliancesRequest':
            response = discover_appliances(request.json)
    elif namespace == 'Control':
        if operation == 'SwitchOnOffRequest':
            response = switch_light(request.json)
        elif operation == 'AdjustNumericalSettingRequest':
            response = set_light_level(request.json)
    elif namespace == 'System':
        if operation == 'HealthCheckRequest':
            response = health_check(request.json)
    else:
        response = generate_error_response(request.json, "UNSUPPORTED_OPERATION", "Unrecognized namespace - " + namespace)

    return jsonify(response)


def discover_appliances(request):
    response = {
        'header': {
            'namespace': 'Discovery',
            'name': 'DiscoverAppliancesResponse',
            'payloadVersion': '1'
        },
        'payload': {
        }
    }

    isy_lights = app.director.get_lights()
    isy_missing_light = {
        'type_model': 'Unknown model',
        'type_desc': 'Unknown device description'
    }

    lights = []
    for light in app.director.lights.values():
        if light.enabled:
            isy_light = isy_lights[light.address] or isy_missing_light
            device = {
                'applianceId': light.address.replace(' ', '_'),
                'manufacturerName': 'Insteon',
                'modelName': isy_light['type_model'],
                'version': isy_light['version'],
                'friendlyName': light.echo_name,
                'friendlyDescription': isy_light['type_desc'],
                'isReachable': not light.missing,
                'additionalApplianceDetails': {
                    'address': light.address
                }
            }
            lights.append(device)

    response['payload']['discoveredAppliances'] = lights
    return response


def switch_light(request):
    pass


def set_light_level(request):
    pass


def health_check(request):
    response = {
        'header': {
            'namespace': 'System',
            'name': 'HealthCheckResponse',
            'payloadVersion': '1'
        },
        'payload': {
            "isHealthy": True,
            "description": "The system is currently healthy"
        }
    }
    return response


def generate_error_response(request, code, message):
    response = {
        'header': {
            'namespace': request['header']['namespace'],
            'name': request['header']['name'].replace('Request', 'Response'),
            'payloadVersion': request['header']['payloadVersion']
        },
        'payload': {
            'exception': {
                'code': code,
                'description': message
            }
        }
    }
    return response
