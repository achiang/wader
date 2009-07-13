# -*- coding: utf-8 -*-
# Copyright (C) 2006-2008  Vodafone España, S.A.
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
"""Common stuff for all Option's datacards/devices"""

import re

from twisted.internet import defer, reactor

from wader.common.command import get_cmd_dict_copy, build_cmd_dict
from wader.common import consts
from wader.common.middleware import WCDMAWrapper
from wader.common.exported import HSOExporter
from wader.common.hardware.base import WCDMACustomizer
from wader.common.aterrors import GenericError
from wader.common.sim import SIMBaseClass
from wader.common.plugin import DevicePlugin
from wader.common.utils import rssi_to_percentage, revert_dict
import wader.common.signals as S

NUM_RETRIES = 30
RETRY_TIMEOUT = 4

OPTION_BAND_MAP_DICT = {
    'ANY'   : consts.MM_NETWORK_BAND_ANY,
    'EGSM'  : consts.MM_NETWORK_BAND_EGSM,
    'DCS'   : consts.MM_NETWORK_BAND_DCS,
    'PCS'   : consts.MM_NETWORK_BAND_PCS,
    'G850'  : consts.MM_NETWORK_BAND_G850,
    'U2100' : consts.MM_NETWORK_BAND_U2100,
    'U1900' : consts.MM_NETWORK_BAND_U1900,
    'U1700' : consts.MM_NETWORK_BAND_U1700,
    '17IV'  : consts.MM_NETWORK_BAND_17IV,
    'U850'  : consts.MM_NETWORK_BAND_U850,
    'U800'  : consts.MM_NETWORK_BAND_U850,
    'U900'  : consts.MM_NETWORK_BAND_U900,
    'U17IX' : consts.MM_NETWORK_BAND_U17IX,
}

OPTION_CONN_DICT = {
    consts.MM_NETWORK_MODE_ANY     : 0,
    consts.MM_NETWORK_MODE_GPRS    : 0,
    consts.MM_NETWORK_MODE_EDGE    : 0,
    consts.MM_NETWORK_MODE_2G_ONLY : 0,

    consts.MM_NETWORK_MODE_UMTS    : 1,
    consts.MM_NETWORK_MODE_HSDPA   : 1,
    consts.MM_NETWORK_MODE_HSUPA   : 1,
    consts.MM_NETWORK_MODE_HSPA    : 1,
    consts.MM_NETWORK_MODE_3G_ONLY : 1,

    consts.MM_NETWORK_MODE_2G_PREFERRED : 2,

    consts.MM_NETWORK_MODE_3G_PREFERRED : 3,
}

# The option band dictionary does not need to be specified as we
# modelled the band dict after it

# Option devices like to append its serial number after the IMEI, ignore it
OPTION_CMD_DICT = get_cmd_dict_copy()
OPTION_CMD_DICT['get_imei'] = build_cmd_dict(re.compile(
                                    "\r\n(?P<imei>\d+),\S+\r\n", re.VERBOSE))

OPTION_CMD_DICT['get_sim_status'] = build_cmd_dict(re.compile(r"""
                                             _OBLS:\s(?P<sim>\d),
                                             (?P<contacts>\d),
                                             (?P<sms>\d)
                                             """, re.VERBOSE))

OPTION_CMD_DICT['get_band'] = build_cmd_dict(re.compile(r"""
                                             \r\n(?P<name>.*):\s+(?P<active>\d)
                                             """, re.VERBOSE))

OPTION_CMD_DICT['get_network_mode'] = build_cmd_dict(re.compile(r"""
                                             _OPSYS:\s
                                             (?P<mode>\d),
                                             (?P<domain>\d)
                                             """, re.VERBOSE))

class OptionSIMClass(SIMBaseClass):
    """
    Option SIM Class

    I perform an initial setup in the device and will not
    return until the SIM is *really* ready
    """
    def __init__(self, sconn):
        super(OptionSIMClass, self).__init__(sconn)
        self.num_retries = 0

    def initialize(self, set_encoding=True):
        deferred = defer.Deferred()

        def init_callback(size):
            # make sure we are in 3g pref before registration
            self.sconn.set_network_mode(consts.MM_NETWORK_MODE_3G_PREFERRED)
            # setup asynchronous notifications
            self.sconn.send_at('AT_OSSYS=1') # cell change notification
            self.sconn.send_at('AT_OSQI=1') # signal quality notification
            deferred.callback(size)

        def sim_ready_cb(ignored):
            d2 = super(OptionSIMClass, self).initialize(set_encoding)
            d2.addCallback(init_callback)

        def sim_ready_eb(failure):
            deferred.errback(failure)

        d = self.is_sim_ready()
        d.addCallback(sim_ready_cb)
        d.addErrback(sim_ready_eb)

        return deferred

    def is_sim_ready(self):
        deferred = defer.Deferred()

        def process_sim_state(auxdef):
            def parse_response(resp):
                status = tuple(map(int, resp[0].groups()))
                if status == (1, 1, 1):
                    auxdef.callback(True)
                else:
                    self.num_retries += 1
                    if self.num_retries < NUM_RETRIES:
                        reactor.callLater(RETRY_TIMEOUT,
                                            process_sim_state, auxdef)
                    else:
                        msg = "Max number of attempts reached %d"
                        auxdef.errback(GenericError(msg % self.num_retries))

                return

            self.sconn.send_at('AT_OBLS', name='get_sim_status',
                               callback=parse_response)

            return auxdef

        return process_sim_state(deferred)


def new_conn_mode_cb(args):
    """
    Translates Option's unsolicited notifications to Wader's representation
    """
    ossysi_args_dict = {
        '0' : S.GPRS_SIGNAL,
        '2' : S.UMTS_SIGNAL,
        '3' : S.NO_SIGNAL,
    }
    return ossysi_args_dict[args]


class OptionWrapper(WCDMAWrapper):
    """Wrapper for all Option cards"""

    def _get_band_dict(self):
        """Returns a dict with the available bands and its status"""
        def callback(resp):
            bands = {}

            for r in resp:
                name, active = r.group('name'), int(r.group('active'))
                bands[name] = active

            return bands

        d = self.send_at('AT_OPBM?', name='get_band', callback=callback)
        return d

    def get_band(self):
        """Returns the current used band"""
        def get_band_dict_cb(bands):
            if 'ANY' in bands and bands['ANY'] == 1:
                # can't be combined by design
                return consts.MM_NETWORK_BAND_ANY

            ret = 0
            for name, active in bands.items():
                if not active:
                    continue

                if name in OPTION_BAND_MAP_DICT:
                    ret |= OPTION_BAND_MAP_DICT[name]

            return ret

        d = self._get_band_dict()
        d.addCallback(get_band_dict_cb)
        return d

    def get_network_mode(self):
        """Returns the current network mode"""
        ret_codes = {
            0 : consts.MM_NETWORK_MODE_2G_ONLY,
            1 : consts.MM_NETWORK_MODE_3G_ONLY,
            2 : consts.MM_NETWORK_MODE_2G_PREFERRED,
            3 : consts.MM_NETWORK_MODE_3G_PREFERRED,
            5 : consts.MM_NETWORK_MODE_ANY,
        }
        def callback(resp):
            mode = int(resp[0].group('mode'))
            if mode in ret_codes:
                return ret_codes[mode]

            raise KeyError("Unknown network mode %d" % mode)

        d = self.send_at('AT_OPSYS?', name='get_network_mode',
                         callback=callback)
        return d

    def set_band(self, band):
        """Sets the band to ``band``"""

        def get_band_dict_cb(bands):
            responses = []

            at_str = 'AT_OPBM="%s",%d'

            if band == consts.MM_NETWORK_BAND_ANY:
                if 'ANY' in bands and bands['ANY'] == 1:
                    # if ANY is already enabled, do nothing
                    return defer.succeed(True)

                # enabling ANY will suffice
                responses.append(self.send_at(at_str % ('ANY', 1)))
            else:
                # ANY is not sought, if ANY is enabled we should remove it first
                # bitwise bands
                if 'ANY' in bands and bands['ANY'] == 1:
                    responses.append(self.send_at(at_str % ('ANY', 0)))

                for key, value in OPTION_BAND_MAP_DICT.items():
                    if value == consts.MM_NETWORK_BAND_ANY:
                        # do not attempt to combine it
                        continue

                    if value & band:
                        # enable required band
                        responses.append(self.send_at(at_str % (key, 1)))
                    else:
                        # disable required band
                        responses.append(self.send_at(at_str % (key, 0)))

            if responses:
                dlist = defer.DeferredList(responses, consumeErrors=1)
                dlist.addCallback(lambda l: [x[1] for x in l])
                return dlist

            raise KeyError("OptionWrapper: Unknown band mode %d" % band)

        # due to Option's band API, we'll start by obtaining the current bands
        d = self._get_band_dict()
        d.addCallback(get_band_dict_cb)
        return d

    def set_network_mode(self, mode):
        """Sets the network mode to ``mode``"""
        if mode not in OPTION_CONN_DICT:
            raise KeyError("Unknown mode %d for set_network_mode" % mode)

        value = OPTION_CONN_DICT[mode]
        return self.send_at("AT_OPSYS=%d,2" % value)


class OptionWCDMACustomizer(WCDMACustomizer):
    """Customizer for Option's cards"""
    async_regexp = re.compile(r"""
                \r\n
                (?P<signal>_O[A-Z]{3,}):\s(?P<args>.*)
                \r\n""", re.VERBOSE)
    # the dict is reverted as we are interested in the range of bands
    # that the device supports (get_bands)
    band_dict = revert_dict(OPTION_BAND_MAP_DICT)
    conn_dict = OPTION_CONN_DICT
    cmd_dict = OPTION_CMD_DICT
    device_capabilities = [S.SIG_NETWORK_MODE, S.SIG_RSSI]
    signal_translations = {
        '_OSSYSI' : (S.SIG_NETWORK_MODE, new_conn_mode_cb),
        '_OSIGQ'  : (S.SIG_RSSI, lambda args:
                        (rssi_to_percentage(int(args.split(',')[0]))))
    }
    wrapper_klass = OptionWrapper


class OptionHSOWCDMACustomizer(OptionWCDMACustomizer):
    """Customizer for HSO WCDMA devices"""
    exporter_klass = HSOExporter


class OptionWCDMADevicePlugin(DevicePlugin):
    """DevicePlugin for Option"""
    sim_klass = OptionSIMClass
    custom = OptionWCDMACustomizer()

    def __init__(self):
        super(OptionWCDMADevicePlugin, self).__init__()


class OptionHSOWCDMADevicePlugin(OptionWCDMADevicePlugin):
    """DevicePlugin for Option HSO devices"""
    custom = OptionHSOWCDMACustomizer()

    def __init__(self):
        super(OptionHSOWCDMADevicePlugin, self).__init__()


