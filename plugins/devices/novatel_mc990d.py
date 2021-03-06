# -*- coding: utf-8 -*-
# Copyright (C) 2008-2009  Warp Networks, S.L.
# Author:  Pablo Martí
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

import serial

from wader.common.hardware.novatel import NovatelWCDMADevicePlugin


class NovatelMC990D(NovatelWCDMADevicePlugin):
    """
    :class:`~wader.common.plugin.DevicePlugin` for Novatel MC990D
    """
    name = "Novatel MC990D"
    version = "0.1"
    author = u"Pablo Martí"

    __remote_name__ = "Ovation MC990D Card"

    __properties__ = {
        'ID_VENDOR_ID': [0x1410],
        'ID_MODEL_ID': [0x7001],
    }

    def preprobe_init(self, ports, info):
        # Novatel secondary port needs to be flipped from DM to AT mode
        # before it will answer our AT queries. So the primary port
        # needs this string first or auto detection of ctrl port fails.
        # Note: Early models/firmware were DM only
        ser = serial.Serial(ports[0], timeout=1)
        ser.write('AT$NWDMAT=1\r\n')
        ser.close()
