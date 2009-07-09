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
"""Daemons for Wader"""

from twisted.internet.task import LoopingCall
from twisted.python import log

from wader.common.netspeed import NetworkSpeed
from wader.common.utils import rssi_to_percentage
import wader.common.signals as S

class WaderDaemon(object):
    """
    I represent a Daemon in Wader

    A Daemon is an entity that performs a repetitive action, like polling
    signal quality from the datacard. A Daemon will emit DBus signals as if
    the device itself had emitted them.
    """
    def __init__(self, frequency, device):
        super(WaderDaemon, self).__init__()
        self.frequency = frequency
        self.device = device
        self.loop = None

    def __repr__(self):
        return self.__class__.__name__

    def start(self):
        """Starts the Daemon"""
        log.msg("daemon %s started..." % self.__class__.__name__)
        if not self.loop or not self.loop.running:
            self.loop = LoopingCall(self.function)
            self.loop.start(self.frequency)

            args = (self.__class__.__name__, 'function', self.frequency)
            log.msg("executing %s.%s every %d seconds" % args)

    def stop(self):
        """Stops the Daemon"""
        if self.loop.running:
            cname = self.__class__.__name__
            log.msg("daemon %s stopped..." % cname)
            self.loop.stop()

    def function(self):
        """Function that will be called periodically"""
        raise NotImplementedError()


class SignalQualityDaemon(WaderDaemon):
    """I emit SIG_RSSI UnsolicitedNotifications"""

    def function(self):
        """Executes `get_signal_quality` periodically"""
        d = self.device.sconn.get_signal_quality()
        d.addCallback(rssi_to_percentage)
        d.addCallback(lambda rssi: self.device.exporter.SignalQuality(rssi))


class NetworkSpeedDaemon(WaderDaemon):
    """I emit SIG_SPEED UnsolicitedNotifications"""
    def __init__(self, frequency, device):
        super(NetworkSpeedDaemon, self).__init__(frequency, device)
        self.netspeed = NetworkSpeed()

    def start(self):
        """Starts the network speed measurement process"""
        self.netspeed.start()
        self.loop = LoopingCall(self.function)
        self.loop.start(self.frequency)

    def stop(self):
        """Stops the network speed measurement process"""
        self.loop.stop()
        self.netspeed.stop()

    def function(self):
        """Emits `SpeedChanged` signals every `self.frequency`"""
        up, down = self.netspeed['up'], self.netspeed['down']
        self.device.exporter.SpeedChanged(up, down)


class NetworkRegistrationDaemon(WaderDaemon):
    """
    I monitor several network registration parameters

    I cache, compare and emit if different from previous reading
    """

    def __init__(self, frequency, device):
        super(NetworkRegistrationDaemon, self).__init__(frequency, device)
        self.reading = None

    def function(self):
        d = self.device.sconn.get_netreg_info()
        d.addCallback(self.compare_and_emit_if_different)

    def compare_and_emit_if_different(self, info):
        """
        Compares ``info`` with previously cached value

        If they are different it will emit `RegistrationInfo` signal
        """
        if not self.reading:
            self.reading = info
        else:
            if self.reading == info:
                # nothing has changed
                return

        self.device.exporter.RegistrationInfo(*info)


class WaderDaemonCollection(object):
    """
    I am a collection of Daemons

    I provide some methods to manage the collection.
    """
    def __init__(self):
        self.daemons = {}
        self.running = False

    def append_daemon(self, name, daemon):
        """Adds ``daemon`` to the collection identified by ``name``"""
        self.daemons[name] = daemon

    def has_daemon(self, name):
        """Returns True if daemon ``name`` exists"""
        return name in self.daemons

    def remove_daemon(self, name):
        """Removes daemon with ``name``"""
        del self.daemons[name]

    def start_daemons(self, arg=None):
        """Starts all daemons"""
        for daemon in self.daemons.values():
            daemon.start()

        self.running = True

    def stop_daemon(self, name):
        """Stops daemon identified by ``name``"""
        try:
            self.daemons[name].stop()
        except KeyError:
            raise

    def stop_daemons(self):
        """Stops all daemons"""
        for daemon in self.daemons.values():
            daemon.stop()

        self.running = False


def build_daemon_collection(device):
    """Returns a :class:`WaderServiceCollection` customized for ``device``"""
    collection = WaderDaemonCollection()

    if device.ports.has_two():
        # check capabilities
        if S.SIG_RSSI not in device.custom.device_capabilities:
            # device doesn't sends unsolicited notifications about RSSI
            # changes, we will have to monitor it ourselves every 15s
            freq = 15

            daemon = SignalQualityDaemon(freq, device)
            collection.append_daemon('signal', daemon)

    else:
        # device with just one port will never be able to send us
        # unsolicited notifications, we'll have to fake 'em
        daemon = SignalQualityDaemon(15, device)
        collection.append_daemon('signal', daemon)

    # daemons to be used regardless of ports or capabilities
    daemon = NetworkRegistrationDaemon(120, device)
    collection.append_daemon('netreg', daemon)

    return collection

