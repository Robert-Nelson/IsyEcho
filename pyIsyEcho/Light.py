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
        light = {'address': self.address, 'name': self.name, 'echo_name': self.echo_name, 'enabled': self.enabled}
        return light

    def on(self, director):
        director.isy_controller.execute_node_command(self.address, 'DON', [])
        return

    def off(self, director):
        director.isy_controller.execute_node_command(self.address, 'DOF', [])
        return

    def get_lightlevel(self, director):
        return director.isy_controller.get_node_property(self.address, 'ST')

    def set_lightlevel(self, director, level):
        director.isy_controller.set_node_property(self.address, 'ST', level)
        return
