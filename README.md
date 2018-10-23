# Aura GTK
## GTK interface for configuring lighting on Asus graphics cards.
---
# DISCLAIMER:
THIS HAS THE POSSIBILITY OF BRICKING YOUR DEVICE.

This code has only been tested to work on a single _Asus Strix 1080._
With the Nvidia Proprietary driver version _396.54_

I cannot guarantee that it will work on any other cards.

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
ADAPTER=`i2cdetect -l | grep "NVIDIA i2c adapter 1" | cut -f1 | sed /i2c-//`
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
RED_INTENSITY=0xFF
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
