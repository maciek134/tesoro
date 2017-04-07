# Copyright © 2016 Maciej Sopyło
#
# This file is part of Tesoro Python library.
#
# Tesoro Python library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Tesoro Python library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Tesoro Python library.  If not, see <http://www.gnu.org/licenses/>.

import usb1
import asyncio
from functools import partial

from .defs import *

keyDefs = defs.keyDefs

ERROR_NO_DEVICE = -1 # device not found
ERROR_WRONG_KEY = -2 # key name not found in keyDefs

TYPE_KEYBOARD = 0

def __constructPacket(cmd, profile, *params):
    params = list(params)
    # for convenience, fill with zeros if packet too short
    if len(params) < 5: params = params + [ 0x00 ] * (5 - len(params))

    return bytes([ 0x07, cmd, profile ] + params)

async def __sendControl(dev, data):
    await asyncio.get_event_loop().run_in_executor(None, dev.controlWrite, 0x21, 0x09, 0x0307, 0x01, data)
    await asyncio.sleep(0.01)

async def __asyncSendData(data, productId):
    with usb1.USBContext() as context:
        dev = context.openByVendorIDAndProductID(0x195d, productId, skip_on_error=True)
        if dev == None: return ERROR_NO_DEVICE

        if (dev.kernelDriverActive(1)):
            dev.detachKernelDriver(1)

        for d in range(0, len(data)):
            await __sendControl(dev, data[d])

        # Yo listen up here's a story
        # About an interface I had to claim
        dev.claimInterface(1)
        # Just to release it immediately
        await asyncio.get_event_loop().run_in_executor(None, dev.releaseInterface, 1)
        # So the kernel driver could be attached
        dev.attachKernelDriver(1)
        # Without that crap, media buttons stop working

        dev.close()

        return 0

async def getDeviceList():
    """
    Get connected Tesoro devices
    For now only returns Gram Spectrum
    """
    context = usb1.USBContext()

    devicesList = await asyncio.get_event_loop().run_in_executor(None, partial(context.getDeviceList, skip_on_error=True))
    retList = []

    for dev in devicesList:
        if dev.getVendorID() == 0x195d:
            if dev.getProductID() == 0x2047:
                retList.append({
                    'name': "Gram Spectrum",
                    'bus': dev.getBusNumber(),
                    'address': dev.getDeviceAddress(),
                    'productId': 0x2047,
                    'type': TYPE_KEYBOARD
                })

    return retList


async def setKeyColors(productId, colors, profile):
    """
    Set individual key colors (spectrum mode in original software)

    productId (int)
        product id of the device you want to talk to

    colors (dict)
        dictionary <key>:<color>, where <key> is a key name from defs and <color> is a dict<red,green,blue> or QColor

    profile (int)
        target profile; 1-5 for gaming profiles, 6 for pc mode
    """
    data = [
        __constructPacket(CMD_PROFILE, profile), # set profile (kbd freaks out without it)
        __constructPacket(CMD_COLOR_SPECTRUM, profile, 0xfe, 0x00, 0x00, 0x00, 0x0a) # idk what it does
    ]

    for key in colors.keys():
        if not key in defs.keyDefs: return ERROR_WRONG_KEY
        red = colors[key].red() if colors[key].red else colors[key]['red']
        green = colors[key].green() if colors[key].green else colors[key]['green']
        blue = colors[key].blue() if colors[key].blue else colors[key]['blue']
        data.append(__constructPacket(
            CMD_COLOR_SPECTRUM,
            profile,
            defs.keyDefs[key],
            red,
            green,
            blue,
            0x0a))

    data.append(__constructPacket(CMD_COLOR_SPECTRUM, profile, 0xff, 0x00, 0x00, 0x00, 0xa))

    return await __asyncSendData(data, productId)

async def setMode(productId, mode, profile, submode = 0):
    """
    Set lighting mode
    You don't need to manually switch to spectrum mode before setting keys

    productId (int)
        product id of the device you want to talk to

    mode (int)
        lighting mode; 0 - standard, 1 - trigger, 2 - ripple, 3 - firework, 4 - radiation, 5 - breathing, 6 - rainbow wave, 8 - spectrum colors

    profile (int)
        target profile; 1-5 for gaming profiles, 6 for pc mode

    submode (int)
        sub mode for spectrum colors; 0 - shine, 1 - breathing, 2 - trigger
    """
    data = [
        __constructPacket(CMD_MODE, profile, mode, submode)
    ]

    return await __asyncSendData(data, productId)

async def setColor(productId, color, profile):
    """
    Set whole keyboard color
    This won't set all keys color for spectrum mode!

    productId (int)
        product id of the device you want to talk to

    color (dict)
        dict<red,green,blue> or QColor to set

    profile (int)
        target profile; 1-5 for gaming profiles, 6 for pc mode
    """
    red = color.red() if color.red else color['red']
    green = color.green() if color.green else color['green']
    blue = color.blue() if color.blue else color['blue']
    data = [
        __constructPacket(CMD_COLOR, profile, red, green, blue)
    ]

    return await __asyncSendData(data, productId)

async def setProfile(productId, profile):
    """
    Change active profile

    productId (int)
        product id of the device you want to talk to

    profile (int)
        target profile; 1-5 for gaming profiles, 6 for pc mode
    """
    data = [
        __constructPacket(CMD_PROFILE, profile)
    ]

    return await __asyncSendData(data, productId)
