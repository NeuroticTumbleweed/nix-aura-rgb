"""Module containing aura package main functionality."""

import csv
import logging
from pathlib import Path


import smbus2

logger = logging.getLogger(__name__)

# Default path to the sysfs mount
SYSFS_DEFAULT = Path("/sys")

# Name of the NVIDIA bus which contains the rgb controller.
NVIDIA_RGB_I2C_BUS_NAME = "NVIDIA i2c adapter 1"

# Chip address of the RGB controller.
RGB_CHIP_ADDRESS = 0x29

RED_DATA_ADDRESS = 0x04
# Data addresses of the different red, green, blue and mode registers.
GREEN_DATA_ADDRESS = 0x05
BLUE_DATA_ADDRESS = 0x06
MODE_DATA_ADDRESS = 0x07

# Map of the different effect values.
MODE_MAP = {
    "static": 0x01,
    "breathing": 0x02,
    "blink": 0x03,
    "demo": 0x04
}


def get_color(bus_number=None):
    """Get the current RGB value of the graphics card."""
    # Find the bus number if it's not found.
    if not bus_number:
        bus_number = discover_nvidia_bus()
    with smbus2.SMBusWrapper(bus_number) as bus:
        red = bus.read_byte_data(RGB_CHIP_ADDRESS, RED_DATA_ADDRESS)
        green = bus.read_byte_data(RGB_CHIP_ADDRESS, GREEN_DATA_ADDRESS)
        blue = bus.read_byte_data(RGB_CHIP_ADDRESS, BLUE_DATA_ADDRESS)
    return (red << 16) + (green << 8) + blue


def set_color(rgb: int, bus_number=None):
    """Set the rgb of the graphics card to the given rgb value."""
    # Mask and shift the rgb value to get the individual colors.
    red = (rgb & 0xff0000) >> 16
    green = (rgb & 0x00ff00) >> 8
    blue = rgb & 0x0000ff
    # Find the bus number if it's not found.
    if not bus_number:
        bus_number = discover_nvidia_bus()
    with smbus2.SMBusWrapper(bus_number) as bus:
        bus.write_byte_data(RGB_CHIP_ADDRESS, RED_DATA_ADDRESS, red)
        bus.write_byte_data(RGB_CHIP_ADDRESS, GREEN_DATA_ADDRESS, green)
        bus.write_byte_data(RGB_CHIP_ADDRESS, BLUE_DATA_ADDRESS, blue)


def get_mode(bus_number=None):
    """Get the current mode of the graphics card."""
    # Find the bus number if it's not found.
    if not bus_number:
        bus_number = discover_nvidia_bus()
    with smbus2.SMBusWrapper(bus_number) as bus:
        raw_mode = bus.read_byte_data(RGB_CHIP_ADDRESS, MODE_DATA_ADDRESS)
    for mode, mode_mapped in MODE_MAP.items():
        if raw_mode == mode_mapped:
            return mode


def set_mode(mode: str, bus_number=None):
    """Set the mode of the graphics card to the given mode."""
    # Find the bus number if it's not found.
    if not bus_number:
        bus_number = discover_nvidia_bus()
    raw_mode = MODE_MAP[mode]
    with smbus2.SMBusWrapper(bus_number) as bus:
        bus.write_byte_data(RGB_CHIP_ADDRESS, MODE_DATA_ADDRESS, raw_mode)


def discover_nvidia_bus():
    """Return the i2c bus number of the Nvidia I2C Adapter controlling RGB.

    The i2c bus is identified with device with the name starting with
    'NVIDIA i2c adapter 1'.
    """
    bus_number = None
    for device, name in list_i2c_devices(locate_sysfs()):
        if name.startswith(NVIDIA_RGB_I2C_BUS_NAME):
            bus_number = device.replace("i2c-", "")
            break
    if bus_number is None:
        raise RuntimeError(
            "Could not find an i2c bus matching '{NVIDIA_RGB_I2C_BUS_NAME}'."
        )
    return int(bus_number)


def list_i2c_devices(sysfs: Path) -> [(str, str)]:
    """
    Return a list of i2c device names and numbers.

    :return: list of tuples where the tuple has the form (device, name).
    """
    i2c_dev_base = Path(sysfs, "class/i2c-dev/")
    if not i2c_dev_base.exists():
        raise RuntimeError(
            "Device path {i2c_dev_base} does not exist "
            "under sysfs path: {sysfs}"
        )
    i2c_devices = []
    for device in i2c_dev_base.iterdir():
        device_id = device.name
        with open(Path(device, "name"), "r") as f:
            device_name = f.read().strip()
        i2c_devices.append((device_id, device_name))
    return i2c_devices


def locate_sysfs() -> Path:
    """
    Look in /proc/mount for the sysfs mount point.

    If a sysfs mount point is not specified in /proc/mount return default
    specified by Global SYSFS_DEFAULT.
    :return: Path object of sysfs mount point.
    """
    sysfs = None
    with open("/proc/mounts", "r") as f:
        reader = csv.reader(f, delimiter=" ")
        for row in reader:
            # row[0] is the device
            # row[2] is the file-system type
            if row[0] == "sysfs" and row[2] == "sysfs":
                # row[1] is the mount point
                sysfs = Path(row[1])
    if not sysfs:
        logger.warning(
            f"sysfs not found in /proc/mounts. Using default {SYSFS_DEFAULT}"
        )
        sysfs = SYSFS_DEFAULT
    return sysfs
