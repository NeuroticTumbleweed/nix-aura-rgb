# Aura GTK
## Interface for configuring lighting on Asus graphics cards.
## DISCLAIMER:
THIS HAS THE POSSIBILITY OF BRICKING YOUR DEVICE.

This code has only been tested to work on a single _Asus Strix 1080._
With the Nvidia Proprietary driver version _396.54_

I cannot guarantee that it will work on any other cards.
## Installation:

### Operating system packages
You'll need to install a few operating system level packages:
##### On fedora:
```bash
sudo dnf install python3-gobject python3-dbus
```
##### On Ubuntu/Debian:
```bash
sudo apt-get install python3-gi python3-dbus
```

### Pypi dependencies
Either a python virtualenvironment needs to be set up as root (prefered)
or the lazier but not great way to do things would be to just run:
```bash
sudo pip3 install smbus2
```

### DBus Configuration
DBus needs to be configured to allow the specific users and services to
communicate. This can be done with:
```bash
sudo cp aura.conf /etc/dbus-1/system.d/neurotictumbleweed.aura.conf
```

## Running

Run the daemon as root with:
```bash
sudo python3 aura/dbus_server.py
```

In another terminal, run the GUI with:
```bash
sudo python3 aura/gui.py
```
---

## Bash equivalent:
>__Note__: all of these commands need root privileges

### Discovery:
#### For a list of NVIDIA i2c adapters run:

```bash
i2cdetect -l | grep "NVIDIA i2c adapter"
```
#### To get the specific device number run
```bash
ADAPTER=`i2cdetect -l | grep "NVIDIA i2c adapter 1" | cut -f1 | sed s/i2c-//`
echo ${ADAPTER}
```

#### To verify that the adapter contains the correct devices run:
```bash
sudo i2cdetect ${ADAPTER}
```

The output should look something like this:
```
    0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- 08 -- -- -- -- -- -- --
10: -- -- -- -- -- 15 -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- 29 -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- 68 -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- --
```
It is important that device `29` is detected.

### Setting colors:
Once discovery has been done and the device number has been stored under
`ADAPTER` colors can be set as follows.

#### Setting Red
```bash
RED_INTENSITY=0xFF
i2cset -y ${ADAPTER} 0x29 4 ${RED_INTENSITY}
```

#### Setting Green
```bash
GREEN_INTENSITY=0xFF
i2cset -y ${ADAPTER} 0x29 5 ${GREEN_INTENSITY}
```

#### Setting Blue
```bash
BLUE_INTENSITY=0xFF
i2cset -y ${ADAPTER} 0x29 6 ${BLUE_INTENSITY}
```

### Changing Mode:
There are four modes as summarised in the table:

| Mode     | Value   | Description                                       |
| :------- | ------: | :------------------------------------------------ |
| Static   | 0x01    | Maintains RGB state.                              |
| Breathe  | 0x02    | Breathing effect while maintaining colour.        |
| Blink    | 0x03    | Jarring on and off effect with maintained colour. |
| Demo     | 0x04    | Breathing effect cycling through colours.         |

An example for changing the mode to static would be:
```bash
MODE=0x01
i2cset -y ${ADAPTER} 0x29 7 ${MODE}
```
