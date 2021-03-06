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

from wader.common.hardware.huawei import HuaweiWCDMADevicePlugin


class HuaweiE180(HuaweiWCDMADevicePlugin):
    """:class:`~wader.common.plugin.DevicePlugin` for Huawei's E180"""
    name = "Huawei E180"
    version = "0.1"
    author = u"Pablo Martí"

    __remote_name__ = "E180"

    __properties__ = {
        'ID_VENDOR_ID': [0x12d1],
        'ID_MODEL_ID': [0x1003],
    }
