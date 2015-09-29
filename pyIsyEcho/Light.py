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

        self.address = settings.get("address", None)
        self.name = settings.get("name", "")
        self.echo_name = settings.get("echo_name", "")

        self.enabled = settings.get("enabled", True)
        self.missing = settings.get("missing", False)

    def serialize(self):
        light = {'address': self._address, 'name': self._name, 'echo_name': self._echo_name, 'enabled': self._enabled}
        return light

    def on(self, director):
        director.isy_controller[self.address].on()
        return

    def off(self, director):
        director.isy_controller[self.address].off()
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
