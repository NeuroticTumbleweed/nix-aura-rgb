"""
Expose the color configuration methods over dbus.

The server can be started with:
```bash
python3 dbus_server.py
```

The aura class is then exposed with an interface and can be used as:
```python
import dbus

bus = dbus.SystemBus()
remote_object = bus.get_object("NeuroticTumbleweed.Aura", "/Aura")
aura_interface = dbus.Interface(
    remote_object, "NeuroticTumbleweed.Aura.Interface")
aura_interface.ping()
```
"""
import logging

import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib

from helpers import get_color, set_color, get_mode, set_mode

AURA_INTERFACE = "NeuroticTumbleweed.Aura.Interface"
BUS_NAME = "NeuroticTumbleweed.Aura"

logger = logging.getLogger(__name__)


class AuraException(dbus.DBusException):
    """Add custom AuraException. Not currently used."""
    _dbus_error_name = 'NeuroticTumbleweed.Aura.AuraException'


class Aura(dbus.service.Object):
    """
    Class to expose helper methods over dbus.

    Methods to be configured to be made available over AURA_INTERFACE.
    """

    @dbus.service.method(AURA_INTERFACE)
    def ping(self) -> str:
        """Return "pong" on successful interfacing."""
        logger.info(f"System pinged!")
        return "pong"

    @dbus.service.method(AURA_INTERFACE)
    def get_color(self) -> int:
        """
        Wrap get_color helper method.

        :return: Integer representation of color. 0xRRGGBB
        """
        return get_color()

    @dbus.service.method(AURA_INTERFACE)
    def set_color(self, color: int):
        """
        Wrap set_color helper method.

        :param color: Integer representation of color. 0xRRGGBB
        """
        set_color(color)

    @dbus.service.method(AURA_INTERFACE)
    def get_mode(self) -> str:
        """
        Wrap get_mode method.

        :return: String name of mode currently set.
        """
        return get_mode()

    @dbus.service.method(AURA_INTERFACE)
    def set_mode(self, mode: str):
        """
        Wrap set_mode method.

        :param mode: String name of mode to set. One of:
            ("static", "breathing", "blink", "demo")
        """
        set_mode(mode)


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    logger.info("Starting the Aura dbus server!")
    logger.info("Configuring the main loop.")
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    logger.info("Getting the session bus.")
    bus = dbus.SystemBus()
    logger.info("Registering the bus name.")
    name = dbus.service.BusName(BUS_NAME, bus)

    logger.info("Registering the object.")
    object = Aura(bus, "/Aura")

    mainloop = GLib.MainLoop()
    logger.info(f"Starting the main loop.")
    mainloop.run()
