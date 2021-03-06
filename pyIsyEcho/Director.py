__author__ = 'Robert Nelson'
__copyright__ = 'Copyright (C) 2015 Robert Nelson'
__license__ = 'BSD'

__all__ = ['Director']

import base64
import httplib
import os

from flask import json

from IsySystem import IsySystem

import Light

import logging

logger = logging.getLogger(__package__)

# Source - https://insteon.atlassian.net/wiki/display/IKB/Insteon+Device+Categories+and+Sub-Categories
insteon_devices = {
    '1.0': {'model': '2456D3', 'name': 'LampLinc 3-Pin'},
    '1.1': {'model': '2476D', 'name': 'SwitchLinc Dimmer'},
    '1.2': {'model': '2475D', 'name': 'In-LineLinc Dimmer'},
    '1.3': {'model': '2876DB', 'name': 'ICON Dimmer Switch'},
    '1.4': {'model': '2476DH', 'name': 'SwitchLinc Dimmer (High Wattage)'},
    '1.5': {'model': '2484DWH8', 'name': 'Keypad Countdown Timer w/ Dimmer'},
    '1.6': {'model': '2456D2', 'name': 'LampLinc Dimmer (2-Pin)'},
    '1.7': {'model': '2856D2B', 'name': 'ICON LampLinc'},
    '1.8': {'model': '2476DT', 'name': 'SwitchLinc Dimmer Count-down Timer'},
    '1.9': {'model': '2486D', 'name': 'KeypadLinc Dimmer'},
    '1.10': {'model': '2886D', 'name': 'Icon In-Wall Controller'},
    '1.11': {'model': '2632-422', 'name': 'Insteon Dimmer Module, France (869 MHz)'},
    '1.12': {'model': '2486DWH8', 'name': 'KeypadLinc Dimmer'},
    '1.13': {'model': '2454D', 'name': 'SocketLinc'},
    '1.14': {'model': '2457D2', 'name': 'LampLinc (Dual-Band)'},
    '1.15': {'model': '2632-432', 'name': 'Insteon Dimmer Module, Germany (869 MHz)'},
    '1.17': {'model': '2632-442', 'name': 'Insteon Dimmer Module, UK (869 MHz)'},
    '1.18': {'model': '2632-522', 'name': 'Insteon Dimmer Module, Aus/NZ (921 MHz)'},
    '1.19': {'model': '2676D-B', 'name': 'ICON SwitchLinc Dimmer Lixar/Bell Canada'},
    '1.23': {'model': '2466D', 'name': 'ToggleLinc Dimmer'},
    '1.24': {'model': '2474D', 'name': 'Icon SwitchLinc Dimmer Inline Companion'},
    '1.25': {'model': '2476D', 'name': 'SwitchLinc Dimmer [with beeper]'},
    '1.26': {'model': '2475D', 'name': 'In-LineLinc Dimmer [with beeper]'},
    '1.27': {'model': '2486DWH6', 'name': 'KeypadLinc Dimmer'},
    '1.28': {'model': '2486DWH8', 'name': 'KeypadLinc Dimmer'},
    '1.29': {'model': '2476DH', 'name': 'SwitchLinc Dimmer (High Wattage)[beeper]'},
    '1.30': {'model': '2876DH', 'name': 'ICON Switch Dimmer'},
    '1.31': {'model': '2466Dx', 'name': 'ToggleLinc Dimmer [with beeper]'},
    '1.32': {'model': '2477D', 'name': 'SwitchLinc Dimmer (Dual-Band)'},
    '1.33': {'model': '2472D', 'name': 'OutletLinc Dimmer (Dual-Band)'},
    '1.34': {'model': '2457D2X', 'name': 'LampLinc'},
    '1.35': {'model': '2457D2EZ', 'name': 'LampLinc Dual-Band EZ'},
    '1.36': {'model': '2474DWH', 'name': 'SwitchLinc 2-Wire Dimmer (RF)'},
    '1.37': {'model': '2475DA2', 'name': 'In-LineLinc 0-10VDC Dimmer/Dual-SwitchDB'},
    '1.45': {'model': '2477DH', 'name': 'SwitchLinc-Dimmer Dual-Band 1000W'},
    '1.46': {'model': '2475F', 'name': 'FanLinc'},
    '1.47': {'model': '2484DST6', 'name': 'KeypadLinc Schedule Timer with Dimmer'},
    '1.48': {'model': '2476D', 'name': 'SwitchLinc Dimmer'},
    '1.49': {'model': '2478D', 'name': 'SwitchLinc Dimmer 240V-50/60Hz Dual-Band'},
    '1.50': {'model': '2475DA1', 'name': 'In-LineLinc Dimmer (Dual Band)'},
    '1.52': {'model': '2452-222', 'name': 'Insteon DIN Rail Dimmer (915 MHz)'},
    '1.53': {'model': '2442-222', 'name': 'Insteon Micro Dimmer (915 MHz)'},
    '1.54': {'model': '2452-422', 'name': 'Insteon DIN Rail Dimmer (869 MHz)'},
    '1.55': {'model': '2452-522', 'name': 'Insteon DIN Rail Dimmer (921 MHz)'},
    '1.56': {'model': '2442-422', 'name': 'Insteon Micro Dimmer (869 MHz)'},
    '1.57': {'model': '2442-522', 'name': 'Insteon Micro Dimmer (921 MHz)'},
    '1.58': {'model': '2672-222', 'name': 'LED Bulb 240V (915 MHz) - Screw-in Base'},
    '1.59': {'model': '2672-422', 'name': 'LED Bulb 240V Europe - Screw-in Base'},
    '1.60': {'model': '2672-522', 'name': 'LED Bulb 240V Aus/NZ - Screw-in Base'},
    '1.61': {'model': '2446-422', 'name': 'Insteon Ballast Dimmer (869 MHz)'},
    '1.62': {'model': '2446-522', 'name': 'Insteon Ballast Dimmer (921 MHz)'},
    '1.63': {'model': '2447-422', 'name': 'Insteon Fixture Dimmer (869 MHz)'},
    '1.64': {'model': '2447-522', 'name': 'Insteon Fixture Dimmer (921 MHz)'},
    '1.65': {'model': '2334-222', 'name': 'Keypad Dimmer Dual-Band, 8 Button'},
    '1.66': {'model': '2334-232', 'name': 'Keypad Dimmer Dual-Band, 6 Button'},
    '1.73': {'model': '2674-222', 'name': 'LED Bulb PAR38 US/Can - Screw-in Base'},
    '1.74': {'model': '2674-422', 'name': 'LED Bulb PAR38 Europe - Screw-in Base'},
    '1.75': {'model': '2674-522', 'name': 'LED Bulb PAR38 Aus/NZ - Screw-in Base'},
    '1.76': {'model': '2672-432', 'name': 'LED Bulb 240V Europe - Bayonet Base'},
    '1.77': {'model': '2672-532', 'name': 'LED Bulb 240V Aus/NZ - Bayonet Base'},
    '1.78': {'model': '2674-432', 'name': 'LED Bulb PAR38 Europe - Bayonet Base'},
    '1.79': {'model': '2674-532', 'name': 'LED Bulb PAR38 Aus/NZ - Bayonet Base'},
    '1.80': {'model': '2632-452', 'name': 'Insteon Dimmer Module, Chile (915 MHz)'},
    '1.81': {'model': '2672-452', 'name': 'LED Bulb 240V (915 MHz) - Screw-in Base'},
    '2.5': {'model': '2486SWH8', 'name': 'KeypadLinc 8-button On/Off Switch'},
    '2.6': {'model': '2456S3E', 'name': 'Outdoor ApplianceLinc'},
    '2.7': {'model': '2456S3T', 'name': 'TimerLinc'},
    '2.8': {'model': '2473S', 'name': 'OutletLinc'},
    '2.9': {'model': '2456S3', 'name': 'ApplianceLinc (3-Pin)'},
    '2.10': {'model': '2476S', 'name': 'SwitchLinc Relay'},
    '2.11': {'model': '2876S', 'name': 'ICON On/Off Switch'},
    '2.12': {'model': '2856S3', 'name': 'Icon Appliance Module'},
    '2.13': {'model': '2466S', 'name': 'ToggleLinc Relay'},
    '2.14': {'model': '2476ST', 'name': 'SwitchLinc Relay Countdown Timer'},
    '2.15': {'model': '2486SWH6', 'name': 'KeypadLinc On/Off'},
    '2.16': {'model': '2475S', 'name': 'In-LineLinc Relay'},
    '2.18': {'model': '2474 S/D', 'name': 'ICON In-lineLinc Relay Companion'},
    '2.19': {'model': '2676R-B', 'name': 'ICON SwitchLinc Relay Lixar/Bell Canada'},
    '2.20': {'model': '2475S2', 'name': 'In-LineLinc Relay with Sense'},
    '2.21': {'model': '2476SS', 'name': 'SwitchLinc Relay with Sense'},
    '2.22': {'model': '2876S', 'name': 'ICON On/Off Switch (25 max links)'},
    '2.23': {'model': '2856S3B', 'name': 'ICON Appliance Module'},
    '2.24': {'model': '2494S220', 'name': 'SwitchLinc 220V Relay'},
    '2.25': {'model': '2494S220', 'name': 'SwitchLinc 220V Relay [with beeper]'},
    '2.26': {'model': '2466Sx', 'name': 'ToggleLinc Relay [with Beeper]'},
    '2.28': {'model': '2476S', 'name': 'SwitchLinc Relay'},
    '2.29': {'model': '4101', 'name': 'Commercial Switch with relay'},
    '2.30': {'model': '2487S', 'name': 'KeypadLinc On/Off (Dual-Band)'},
    '2.31': {'model': '2475SDB', 'name': 'In-LineLinc On/Off (Dual-Band)'},
    '2.37': {'model': '2484SWH8', 'name': 'KeypadLinc 8-Button Countdown On/Off Switch Timer'},
    '2.38': {'model': '2485SWH6', 'name': 'Keypad Schedule Timer with On/Off Switch'},
    '2.41': {'model': '2476ST', 'name': 'SwitchLinc Relay Countdown Timer'},
    '2.42': {'model': '2477S', 'name': 'SwitchLinc Relay (Dual-Band)'},
    '2.43': {'model': '2475SDB-50', 'name': 'In-LineLinc On/Off (Dual Band, 50/60 Hz)'},
    '2.44': {'model': '2487S', 'name': 'KeypadLinc On/Off (Dual-Band,50/60 Hz)'},
    '2.45': {'model': '2633-422', 'name': 'Insteon On/Off Module, France (869 MHz)'},
    '2.46': {'model': '2453-222', 'name': 'Insteon DIN Rail On/Off (915 MHz)'},
    '2.47': {'model': '2443-222', 'name': 'Insteon Micro On/Off (915 MHz)'},
    '2.48': {'model': '2633-432', 'name': 'Insteon On/Off Module, Germany (869 MHz)'},
    '2.49': {'model': '2443-422', 'name': 'Insteon Micro On/Off (869 MHz)'},
    '2.50': {'model': '2443-522', 'name': 'Insteon Micro On/Off (921 MHz)'},
    '2.51': {'model': '2453-422', 'name': 'Insteon DIN Rail On/Off (869 MHz)'},
    '2.52': {'model': '2453-522', 'name': 'Insteon DIN Rail On/Off (921 MHz)'},
    '2.53': {'model': '2633-442', 'name': 'Insteon On/Off Module, UK (869 MHz)'},
    '2.54': {'model': '2633-522', 'name': 'Insteon On/Off Module, Aus/NZ (921 MHz)'},
    '2.55': {'model': '2635-222', 'name': 'Insteon On/Off Module, US (915 MHz)'},
    '2.56': {'model': '2634-222', 'name': 'On/Off Outdoor Module (Dual-Band)'},
    '2.57': {'model': '2663-222', 'name': 'On/Off Outlet'},
    '2.58': {'model': '2633-452', 'name': 'Insteon On/Off Module, Chile (915 MHz)'}
}


class Director(object):
    def __init__(self, **kwargs):
        # print('Director ', self.__class__.__name__)

        self.debug = kwargs.get('debug', False)
        self._config_path = kwargs.get('config_path', '.')
        self._shut_down = 0
        self._on = False

        self._secret_key = None

        self._Isy_Url = ''
        self._Isy_User = ''
        self._Isy_Pass = ''

        self.username = ''
        self.password = ''

        self.amazon_email = ''

        self._lights = {}

        self._isy_controller = None
        self._isy_lights = None

        self.token = None

    @property
    def settings(self):
        return {'IsyUrl': self._Isy_Url, 'IsyUser': self._Isy_User, 'IsyPass': self._Isy_Pass,
                'Username': self.username, 'Password': self.password, 'AmazonEmail': self.amazon_email,
                'SecretKey': self._secret_key}

    def update_settings(self, settings):
        if (settings['IsyUrl'] != self._Isy_Url or settings['IsyUser'] != self._Isy_User or
                settings['IsyPass'] != self._Isy_Pass):

            self._Isy_Url = settings['IsyUrl']
            self._Isy_User = settings['IsyUser']
            self._Isy_Pass = settings['IsyPass']
            self.start_controller()

        if (settings['Username'] != self.username or settings['Password'] != self.password or
                settings['AmazonEmail'] != self.amazon_email):
            self.username = settings['Username']
            self.password = settings['Password']
            self.amazon_email = settings['AmazonEmail']

    @property
    def settings_complete(self):
        return (len(self._Isy_Url) > 0 and len(self._Isy_User) > 0 and len(self._Isy_Pass) > 0 and
                len(self.username) > 0 and len(self.password) > 0 and len(self.amazon_email) > 0)

    @property
    def secret_key(self):
        if self._secret_key is None:
            self._secret_key = os.urandom(32)
            self.save_config()
        return self._secret_key

    @property
    def isy_controller(self):
        return self._isy_controller

    @property
    def lights(self):
        return self._lights

    def load_config(self):
        try:
            config_fp = open(os.path.join(self._config_path, 'ISYEcho.json'))
            config = json.load(config_fp)
            config_fp.close()
        except IOError:
            config = {}

        secret_key = config.get('SecretKey')

        if secret_key is not None:
            self._secret_key = base64.b64decode(secret_key)
        else:
            self._secret_key = None

        self._Isy_Url = config.get('IsyUrl', '')
        #if self._Isy_Url == '':
        #    from ISY.IsyDiscover import isy_discover
        #    result = isy_discover(timeout=30, count=1)
        #    if len(result) == 1:
        #        import urlparse
        #        self._Isy_Url = urlparse.urlparse(result.values()[0]['URLBase']).netloc

        self._Isy_User = config.get('IsyUser', '')
        self._Isy_Pass = config.get('IsyPass', '')

        self.username = config.get('Username', '')
        self.password = config.get('Password', '')

        self.amazon_email = config.get('AmazonEmail', '')

        for light_cfg in config.get('lights', {}):
            light = Light.Light(settings=light_cfg)
            self._lights[light.address] = light

    def save_config(self):
        config = self.settings.copy()
        config['SecretKey'] = base64.b64encode(self._secret_key)
        if len(self._lights) > 0:
            config['lights'] = []
            for light_address in sorted(self._lights):
                config['lights'].append(self._lights[light_address].serialize())
        config_fp = open(os.path.join(self._config_path, 'ISYEcho.json'), 'w')
        json.dump(config, config_fp, indent=4, separators=(',', ': '), sort_keys=True)
        config_fp.write('\n')
        config_fp.close()

    def update_lights(self, lights):
        for index in lights:
            light_cfg = lights[index]
            light = self._lights[light_cfg['address']]
            light.enabled = 'enabled' in light_cfg
            light.echo_name = light_cfg['echo_name']

    def start(self):
        self.load_config()
        self.start_controller()

    def start_controller(self):
        if len(self._Isy_Url) > 0 and len(self._Isy_User) > 0 and len(self._Isy_Pass) > 0:
            self._isy_controller = IsySystem(url=self._Isy_Url, user=self._Isy_User, password=self._Isy_Pass)

        if self._isy_controller:
            isy_lights = self.get_lights()
            for address in self._lights:
                if address not in isy_lights:
                    self._lights[address].missing = True
            for isy_light in isy_lights:
                if isy_light not in self._lights:
                    light = Light.Light()
                    light.address = isy_light
                    light.name = isy_lights[isy_light]['name']
                    light.echo_name = isy_lights[isy_light]['name']
                    self._lights[isy_light] = light

    def get_lights(self):
        if self._isy_lights is None:
            self._isy_lights = {}
            nodes = self._isy_controller.get_nodes()
            for node in nodes['result']:
                category, subcat, version, other = node['type'].split('.')
                if category == '1' or category == '2':
                    if node['address'] == node['pnode']:
                        if 'family' not in node:
                            node_info = {
                                'name': node['name'],
                                'type': node['type'],
                                'address': node['address'],
                                'version': version
                            }
                            node_type_info = insteon_devices.get(category + '.' + subcat)
                            if node_type_info is not None:
                                node_info['type_desc'] = node_type_info['name']
                                node_info['type_model'] = node_type_info['model']
                            else:
                                node_info['type_desc'] = 'Node type = ' + node['type']
                                node_info['type_model'] = 'Unknown model'
                            self._isy_lights[node_info['address']] = node_info
                        else:
                            logger.debug('skipping node %s, family %s', node['name'], node['family'])
                    else:
                        logger.debug('skipping node %s, sub-device', node['name'])
                else:
                    logger.debug('skipping node %s, unsupported', node['name'])
        return self._isy_lights

    def validate_access(self, token):
        if token == self.token:
            return True
        conn = httplib.HTTPSConnection('www.amazon.com')
        conn.request('GET', '/ap/user/profile?access_token=' + token)
        resp = conn.getresponse()
        logger.debug('status = %s, reason = %s', resp.status, resp.reason)
        if resp.status == 200:
            data = resp.read()
            logger.debug('data = ' + data)
            profile = json.loads(data)
            email = profile['Profile']['PrimaryEmail']
            logger.debug('email = %s', email)
            if email == self.amazon_email:
                self.token = token
                return True
        return False
