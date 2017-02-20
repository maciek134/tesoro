# tesoro
Python 3 library for interfacing with Tesoro hardware

# Status
This is still a work in progress. Basic functionality for lighting management is
there, but no support for macros / key rebinding / auto profile switching.

I will be adding these features, but in the mean time keep in mind that the API
**will** change until I hit 1.x release (for example now there is no way to
use it with another hardware, because productId is hardcoded)!

I don't intend to add Python 2 compatibility, I believe software should move
forward and supporting older versions is against that belief.

Also it's only tested on Tesoro Gram Spectrum, because that's the only one I have.
I'm not sure if the protocol differs between different devices (like Razer does),
but command ids are probably different. If you have other hardware I can write a
guide on how to capture USB packets so I can implement support for your device
(if you know how to do that yourself even better! just create an issue in the
 tracker with captures attached).

# Known issues
After any call media buttons stop working - probably something is wrong with
reattaching the kernel driver - unplugging and plugging the keyboard back fixes
the issue.

# Documentation
If you don't want to call the script with root privileges and your system uses `udev`
add yourself to the `plugdev` group and create a file `/lib/udev/rules.d/85-tesoro-config.rules`:
```
ACTION=="add", SUBSYSTEMS=="usb", ATTRS{idVendor}=="195d", ATTRS{idProduct}=="2047", MODE="660", GROUP="plugdev"
```
Tested on Ubuntu 16.10 with Tesoro Gram Spectrum, change `idProduct` for other
hardware.

A new thread is created for each call and locking mechanism is used to make sure
no commands mix with each other. I may switch to one thread in the future.

All color related methods accept either a dictionary with `'red','green','blue'`
keys set to `int` values (`0x00`-`0xff`) or a QColor from PyQt5.

Key definitions are in the `defs.py` file. I tried to figure out if there was
some logic to it, but didn't see any - if you see some pattern in there let me know,
I'd be glad to replace the dictionary with some nice function. For method calls
you only need their names, and they are based on `xdotool`'s key names.

Method definitions:

## tesoro.setProfile(profile)
Changes active profile.

**profile**: integer id of the profile; 1-5 for gaming profiles, 6 for pc mode

## tesoro.setColor(color, profile)
Sets the color used for standard lighting effects
__This won't set all keys color for spectrum mode!__

**color**: `dict<red,green,blue>` or `QColor` to set
**profile**: integer denoting current profile; 1-5 for gaming profiles, 6 for pc mode

## setMode(mode, profile, submode = 0)
Set lighting mode
__When setting colors in spectrum mode the keyboard will switch to it automatically,
so no need to call this function unless you want to change the submode.__

**mode**: lighting mode; 0 - standard, 1 - trigger, 2 - ripple, 3 - firework, 4 - radiation, 5 - breathing, 6 - rainbow wave, 8 - spectrum colors
**profile**: integer denoting current profile; 1-5 for gaming profiles, 6 for pc mode
**submode**: sub mode for spectrum colors; 0 - shine, 1 - breathing, 2 - trigger; 0 for standard modes

## setKeyColors(colors, profile)
Set individual key colors (spectrum mode in original software)

**colors**: dictionary <key>:<color>, where <key> is a key name from `defs.py` and <color> is a dict<red,green,blue> or QColor
**profile**: integer denoting current profile; 1-5 for gaming profiles, 6 for pc mode
