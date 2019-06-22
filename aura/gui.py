#!/usr/bin/env python3
"""GUI for the aura GTK."""
import sys

import dbus
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk  # noqa: E401

try:
    BUS = dbus.SystemBus()
    REMOTE_OBJECT = BUS.get_object("NeuroticTumbleweed.Aura", "/Aura")
    AURA_INTERFACE = dbus.Interface(
        REMOTE_OBJECT, "NeuroticTumbleweed.Aura.Interface")
    AURA_INTERFACE.ping()
except Exception as e:  # TODO: Make this more specific
    message_dialog = Gtk.MessageDialog(
        title="Aura Gtk Error",
        text="An error occured connecting to the aura service.",
        secondary_text=f"Traceback:\n {e}",
        buttons=["Exit Aura Gtk", Gtk.ButtonsType.CLOSE],
        )
    message_dialog.run()
    # message_dialog.run()
    print(f"dbus failed: {e}")
    sys.exit()


class GtkMainWindow(Gtk.Window):
    """Main Window of the AuraGtk Application."""

    EFFECTS = (
        ("Static", "static"),
        ("Breathing", "breathing"),
        ("Blink", "blink"),
        ("Demo", "demo")
    )

    def __init__(self):
        """Initialise the AuraGtk Application Window."""
        super().__init__(title="Aura Gtk")
        self.vbox = Gtk.VBox(spacing=20)
        self.box = Gtk.Box(spacing=20)
        self.add(self.vbox)

        self.set_titlebar(self.HeaderBar())
        button_grid = Gtk.Grid()
        buttons = self._create_radio_buttons()
        for index, button in enumerate(buttons):
            button_grid.attach(button, 0, index, 1, 1)
        self.box.pack_start(button_grid, True, False, 0)

        color_box = Gtk.Box()
        color_box.set_size_request(80, 80)
        color_box.pack_start(self.ColorButton(), True, True, 0)
        self.box.pack_end(color_box, True, False, 0)

        self.vbox.pack_start(self.box, True, False, 20)
        # self.set_resizable(False)

    class HeaderBar(Gtk.HeaderBar):
        """Header Bar for the main window."""

        def __init__(self):
            """Customise the title bar."""
            super().__init__()
            self.set_title("Aura Gtk")
            self.set_subtitle("Configure Asus RGB Lighting")
            self.set_show_close_button(True)

    class ColorButton(Gtk.ColorButton):
        """Color Button to pick RGB color."""

        def __init__(self):
            """Customise the color button."""
            super().__init__()
            self.connect("color-set", self.set_device_color)
            self.set_use_alpha(False)
            self.set_rgba(self.get_device_color())

        def get_device_color(self):
            color = Gdk.RGBA()
            color.parse(hex(AURA_INTERFACE.get_color()).replace("0x", "#"))
            return color

        def set_device_color(self, color_button):
            gdk_rgba = color_button.get_rgba()
            red = round(gdk_rgba.red * 255)
            green = round(gdk_rgba.green * 255)
            blue = round(gdk_rgba.blue * 255)
            rgb = (red << 16) + (green << 8) + blue
            AURA_INTERFACE.set_color(rgb)

    def _create_radio_buttons(self):
        buttons = []
        previous_button = None
        for pretty_name, name_value in self.EFFECTS:
            button = Gtk.RadioButton.new_with_label_from_widget(
                previous_button, pretty_name
            )
            button.connect("toggled", self.on_button_toggled, name_value)
            buttons.append(button)
            previous_button = button
        return buttons

    def on_button_toggled(self, button, name):
        if button.get_active():
            AURA_INTERFACE.set_mode(name)


if __name__ == '__main__':

    win = GtkMainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
