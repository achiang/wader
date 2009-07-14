# -*- coding: utf-8 -*-
# Copyright (C) 2006-2009  Vodafone España, S.A.
# Author: Pablo Martí
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from wader.common.hardware.novatel import NovatelWCDMADevicePlugin
import serial

class NovatelXU870(NovatelWCDMADevicePlugin):
    """:class:`~wader.common.plugin.DevicePlugin` for Novatel's XU870"""
    name = "Novatel XU870"
    version = "0.1"
    author = u"Pablo Martí"

    __remote_name__ = "Merlin XU870 ExpressCard"

    __properties__ = {
        'usb_device.vendor_id' : [0x1410],
        'usb_device.product_id' : [0x1430],
    }

    def preprobe_init(self, ports, info):
        # Novatel secondary port needs to be flipped from DM to AT mode
        # before it will answer our AT queries. So the primary port
        # needs this string first or auto detection of ctrl port fails.
        # Note: Early models/firmware were DM only
        ser = serial.Serial(ports[0], timeout=1)
        ser.write('AT$NWDMAT=1\r\n')
        ser.close()

novatelxu870 = NovatelXU870()
