__author__ = 'Robert Nelson'
__copyright__ = "Copyright (C) 2014 Robert Nelson"
__license__ = "BSD"

__all__ = ['Light']

import logging
import random

logger = logging.getLogger(__package__)


class Light(object):
    def __init__(self, **kwargs):
        # logger.debug("Light ", self.__class__.__name__)

        self.debug = kwargs.get("debug", 0)

        settings = kwargs.get("settings", {})

        self._address = settings.get("address", None)
        self._name = settings.get("name", "")
        self._echo_name = settings.get("echo_name", "")

        self._enabled = settings.get("enabled", True)
        self._missing = settings.get("missing", False)

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def echo_name(self):
        return self._echo_name

    @echo_name.setter
    def echo_name(self, value):
        self._echo_name = value

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value

    @property
    def missing(self):
        return self._missing

    @missing.setter
    def missing(self, value):
        self._missing = value

    def serialize(self):
        light = {'address': self._address, 'name': self._name, 'echo_name': self._echo_name, 'enabled': self._enabled}
        return light

    def on(self, director):
        return

    def off(self, director):
        return

    def set_lightlevel(self, director, level):
        return
        # if not self._ignore_status:
        #     if level == 255:
        #         self.on(director, False)
        #     elif level == 0:
        #         self.off(director)
        # else:
        #     self._ignore_status = False
