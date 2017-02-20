import threading
import time
import usb1
from copy import deepcopy

from .defs import *

keyDefs = defs.keyDefs

sendLock = threading.Lock()

class __SendThread(threading.Thread):
    """Class for sendinig data to the keyboard

    Needed because there must be a pause between commands sent and if I have to
    use anything from `threading` module I may as well write my own Thread subclass.
    """
    def __init__(self, vendorId, productId, data, args=(), kwargs=None):
        """Initiate the class

            :param vendorId: Vendor ID of the keyboard
            :param productId: Product ID of the keyboard
            :param data: data to send, see ``defs.py`` for structure
        """
        threading.Thread.__init__(self, args=args, kwargs=kwargs)
        self.context = usb1.USBContext()

        sendLock.acquire()
        self.dev = self.context.openByVendorIDAndProductID(vendorId,
                                                           productId,
                                                           skip_on_error=True)
        self.data = data

    def run(self):

        wasActive = False

        # check if kernel driver was attached to the interface
        # (sometimes it isn't!)
        if (self.dev.kernelDriverActive(1)):
            self.dev.detachKernelDriver(1)
            wasActive = True

        for packet in self.data:
            self.dev.controlWrite(0x21, 0x09, 0x0307, 0x01, packet)
            # timeout needed because kbd's CPU can't handle data that fast
            # and we are in a thread anyway so no harm in a little .sleep
            time.sleep(0.01)

        # reattach the kernel driver if it was attached in the first place
        if wasActive:
            self.dev.attachKernelDriver(1)

        self.dev.close()

        sendLock.release()

def __constructPacket(cmd, profile, *params):
    params = list(params)
    # for convenience, fill with zeros if packet too short
    if len(params) < 5: params = params + [ 0x00 ] * (5 - len(params))

    return bytes([ 0x07, cmd, profile ] + params)

def __sendData(data):
    thread = __SendThread(0x195d, 0x2047, data)
    thread.start()

def setKeyColors(colors, profile):
    """Set individual key colors (spectrum mode in original software)

        :param colors: dictionary <key>:<color>, where <key> is a key name from defs and <color> is a dict<red,green,blue> or QColor
        :param profile: integer denoting current profile; 1-5 for gaming profiles, 6 for pc mode
    """
    data = [
        __constructPacket(defs.cmd['profile'], profile), # set profile (kbd freaks out without it)
        __constructPacket(defs.cmd['colorSpectrum'], profile, 0xfe, 0x00, 0x00, 0x00, 0x0a) # idk what it does
    ]

    for key in colors.keys():
        red = colors[key].red() if colors[key].red else colors[key]['red']
        green = colors[key].green() if colors[key].green else colors[key]['green']
        blue = colors[key].blue() if colors[key].blue else colors[key]['blue']
        data.append(__constructPacket(
            defs.cmd['colorSpectrum'],
            profile,
            defs.keyDefs[key],
            red,
            green,
            blue,
            0x0a))

    data.append(__constructPacket(defs.cmd['colorSpectrum'], profile, 0xff, 0x00, 0x00, 0x00, 0xa))

    __sendData(data)

def setMode(mode, profile, submode = 0):
    """Set lighting mode
        :note You don't need to manually switch to spectrum mode before setting keys

        :param mode: lighting mode; 0 - standard, 1 - trigger, 2 - ripple, 3 - firework, 4 - radiation, 5 - breathing, 6 - rainbow wave, 8 - spectrum colors
        :param profile: integer denoting current profile; 1-5 for gaming profiles, 6 for pc mode
        :param submode: sub mode for spectrum colors; 0 - shine, 1 - breathing, 2 - trigger
    """
    data = [
        __constructPacket(defs.cmd['mode'], profile, mode, submode)
    ]

    __sendData(data)

def setColor(color, profile):
    """Set whole keyboard color
        :note This won't set all keys color for spectrum mode!

        :param color: dict<red,green,blue> or QColor to set
        :param profile: integer denoting current profile; 1-5 for gaming profiles, 6 for pc mode
    """
    red = color.red() if color.red else color['red']
    green = color.green() if color.green else color['green']
    blue = color.blue() if color.blue else color['blue']
    data = [
        __constructPacket(defs.cmd['color'], profile, red, green, blue)
    ]

    __sendData(data)

def setProfile(profile):
    """Change active profile

        :param profile: integer denoting current profile; 1-5 for gaming profiles, 6 for pc mode
    """
    data = [
        __constructPacket(defs.cmd['profile'], profile)
    ]

    __sendData(data)
