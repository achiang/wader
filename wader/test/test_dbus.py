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
"""
Self-contained unittest suite for ModemManager implementations
"""

# install the following packages on Ubuntu
# python-dbus, python-gconf, python-gobject, python-twisted-core
#
# install the following packages On OpenSuSE
# dbus-1-python, python-gnome, python-gobject2, python-twisted
#
# to run the tests:
# trial -e -r glib2 --tbformat=verbose /path/to/test_dbus.py

import os
import random
import re
import sys
import time

import dbus
import dbus.mainloop.glib
import gconf
from twisted.internet import defer
from twisted.trial import unittest

MM_SERVICE = 'org.freedesktop.ModemManager'
MM_OBJPATH = '/org/freedesktop/ModemManager'
MM_INTFACE = MM_SERVICE

MDM_INTFACE = 'org.freedesktop.ModemManager.Modem'
SPL_INTFACE = 'org.freedesktop.ModemManager.Modem.Simple'
CRD_INTFACE = 'org.freedesktop.ModemManager.Modem.Gsm.Card'
CTS_INTFACE = 'org.freedesktop.ModemManager.Modem.Gsm.Contacts'
SMS_INTFACE = 'org.freedesktop.ModemManager.Modem.Gsm.SMS'
NET_INTFACE = 'org.freedesktop.ModemManager.Modem.Gsm.Network'

MM_NETWORK_BAND_UNKNOWN = 0x0     # Unknown or invalid band
MM_NETWORK_BAND_ANY = 0x1     # ANY
MM_NETWORK_BAND_EGSM = 0x2     # 900 MHz
MM_NETWORK_BAND_DCS = 0x4     # 1800 MHz
MM_NETWORK_BAND_PCS = 0x8     # 1900 MHz
MM_NETWORK_BAND_G850 = 0x10    #  850 MHz
MM_NETWORK_BAND_U2100 = 0x20    # WCDMA 2100 MHz
MM_NETWORK_BAND_U1700 = 0x40    # WCDMA 3GPP UMTS1800 MHz
MM_NETWORK_BAND_17IV = 0x80    # WCDMA 3GPP AWS 1700/2100 MHz
MM_NETWORK_BAND_U800 = 0x100   # WCDMA 3GPP UMTS800 MHz
MM_NETWORK_BAND_U850 = 0x200   # WCDMA 3GPP UMTS850 MHz
MM_NETWORK_BAND_U900 = 0x400   # WCDMA 3GPP UMTS900 MHz
MM_NETWORK_BAND_U17IX = 0x800   # WCDMA 3GPP UMTS MHz
MM_NETWORK_BAND_U1900 = 0x1000  # WCDMA 3GPP UMTS MHz

MM_NETWORK_BANDS = [
    MM_NETWORK_BAND_UNKNOWN,
    MM_NETWORK_BAND_ANY,
    MM_NETWORK_BAND_EGSM,
    MM_NETWORK_BAND_DCS,
    MM_NETWORK_BAND_PCS,
    MM_NETWORK_BAND_G850,
    MM_NETWORK_BAND_U2100,
    MM_NETWORK_BAND_U1700,
    MM_NETWORK_BAND_17IV,
    MM_NETWORK_BAND_U800,
    MM_NETWORK_BAND_U850,
    MM_NETWORK_BAND_U900,
    MM_NETWORK_BAND_U17IX,
    MM_NETWORK_BAND_U1900]

MM_NETWORK_MODE_UNKNOWN = 0x00000000
MM_NETWORK_MODE_ANY = 0x00000001
MM_NETWORK_MODE_GPRS = 0x00000002
MM_NETWORK_MODE_EDGE = 0x00000004
MM_NETWORK_MODE_UMTS = 0x00000008
MM_NETWORK_MODE_HSDPA = 0x00000010
MM_NETWORK_MODE_2G_PREFERRED = 0x00000020
MM_NETWORK_MODE_3G_PREFERRED = 0x00000040
MM_NETWORK_MODE_2G_ONLY = 0x00000080
MM_NETWORK_MODE_3G_ONLY = 0x00000100
MM_NETWORK_MODE_HSUPA = 0x00000200
MM_NETWORK_MODE_HSPA = 0x00000400

# should the extensions introduced by the Wader project be tested?
TEST_WADER_EXTENSIONS = True
# generic message for [wader] skipped tests
GENERIC_SKIP_MSG = "Wader extension to MM"
GCONF_BASE = '/apps/wader-core'

if dbus.version >= (0, 83, 0):

    def get_dbus_error(e):
        return e.get_dbus_name()
else:

    def get_dbus_error(e):
        return e.message

def get_bands(bitwised_band):
    """Returns all the bitwised bands in ``bitwised_band``"""
    return [band for band in MM_NETWORK_BANDS if band & bitwised_band]

class Config(object):
    """Simple GConf wrapper for string-only gets"""

    def __init__(self, path):
        self.path = path
        self.client = gconf.client_get_default()

    def get(self, section, key, default=None):
        path = os.path.join(self.path, section, key)
        value = self.client.get(path)
        if not value:
            return (default if default is not None else "")

        assert value.type == gconf.VALUE_STRING, "Unhandled type"
        return value.get_string()


config = Config(GCONF_BASE)

# ==================================================
#                    ATTENTION
# ==================================================
# in order to store the PIN in gconf for testing run
# gconftool-2 -s -t string /apps/wader-core/test/pin 0000
# gconftool-2 -s -t string /apps/wader-core/test/phone 876543210
#
# edit the GCONF_BASE variable above, to change the '/apps/wader-core'

class DBusTestCase(unittest.TestCase):
    """Test-suite for ModemManager DBus exported methods"""

    def setUpClass(self):
        # setUpClass is meant to be deprecated, and setUp should be
        # used instead, however setUp's behaviour doesn't replicates
        # setUpClass' one, so for now we're going to use this
        # Twisted deprecated function
        d = defer.Deferred()
        self.device = None

        loop = dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus(mainloop=loop)

        def enable_device_cb():
            # if we don't sleep for a sec, the test will start too soon
            # and Enable won't be finished yet, yielding spurious results.
            time.sleep(1)
            d.callback(True)

        def enable_device_eb(e):
            if 'SimPinRequired' in get_dbus_error(e):
                pin = config.get('test', 'pin', '0000')
                self.device.SendPin(pin, dbus_interface=CRD_INTFACE,
                                    reply_handler=enable_device_cb,
                                    error_handler=d.errback)
            else:
                raise unittest.SkipTest("Cannot handle error %s" % e)

        def get_device_from_opath(opaths):
            if not len(opaths):
                raise unittest.SkipTest("Can't run this test without devices")

            self.device = bus.get_object(MM_SERVICE, opaths[0])
            # enable the device
            self.device.Enable(True, dbus_interface=MDM_INTFACE,
                               reply_handler=enable_device_cb,
                               error_handler=enable_device_eb)

        obj = bus.get_object(MM_SERVICE, MM_OBJPATH)
        obj.EnumerateDevices(dbus_interface=MM_INTFACE,
                             reply_handler=get_device_from_opath,
                             error_handler=d.errback)
        return d

    def tearDownClass(self):
        d = defer.Deferred()
        # disable device at the end of the test
        self.device.Enable(False,
                           dbus_interface=MDM_INTFACE,
                           reply_handler=lambda: d.callback(True),
                           error_handler=d.errback)
        return d

    # org.freedesktop.ModemManager.Modem tests
    def test_ModemDeviceProperty(self):
        if sys.platform != 'linux2':
            raise unittest.SkipTest("Cannot be tested on OS != Linux")

        device = self.device.Get(MDM_INTFACE, 'Device',
                                 dbus_interface=dbus.PROPERTIES_IFACE)
        self.failUnlessIsInstance(device, basestring)
        self.failUnless('tty' in device)

    def test_ModemMasterDeviceProperty(self):
        master_device = self.device.Get(MDM_INTFACE, 'MasterDevice',
                                        dbus_interface=dbus.PROPERTIES_IFACE)
        # XXX: MasterDevice property not implemented in core
        self.failUnlessIsInstance(master_device, basestring)

    def test_ModemDriverProperty(self):
        if sys.platform != 'linux2':
            raise unittest.SkipTest("Cannot be tested on OS != Linux")

        driver = self.device.Get(MDM_INTFACE, 'Driver',
                                 dbus_interface=dbus.PROPERTIES_IFACE)
        # XXX: Am I missing any driver ?
        self.failUnlessIn(driver, ['hso', 'option', 'mbm', 'sierra',
                                   'cdc_ether', 'cdc_wdm'])

    def test_ModemTypeProperty(self):
        _type = self.device.Get(MDM_INTFACE, 'Type',
                                dbus_interface=dbus.PROPERTIES_IFACE)
        self.failUnlessIsInstance(_type, (int, dbus.UInt32))
        self.failUnlessIn(_type, [1, 2])

    def test_ModemIpMethodProperty(self):
        method = self.device.Get(MDM_INTFACE, 'IpMethod',
                                 dbus_interface=dbus.PROPERTIES_IFACE)
        # XXX: IpMethod property hardcoded to 1 (static)
        self.failUnlessIsInstance(method, (int, dbus.UInt32))
        self.failUnlessIn(method, [0, 1, 2])

    def test_ModemGetInfo(self):
        """Test for Modem.GetInfo"""
        d = defer.Deferred()

        def get_info_cb(info):
            self.failUnless(len(info) == 3)
            self.failUnlessIsInstance(info[0], basestring)
            self.failUnlessIsInstance(info[1], basestring)
            self.failUnlessIsInstance(info[2], basestring)
            d.callback(True)

        self.device.GetInfo(dbus_interface=MDM_INTFACE,
                            reply_handler=get_info_cb,
                            error_handler=d.errback)
        return d

    # org.freedesktop.ModemManager.Modem.Gsm.Card tests
    def test_CardChangePin(self):
        """Test for Card.ChangePin"""
        d = defer.Deferred()
        good_pin = config.get('test', 'pin', '0000')
        bad_pin = '1111'

        def pin_changed_cb():
            self.device.ChangePin(bad_pin, good_pin,
                                  dbus_interface=CRD_INTFACE,
                                  # test finishes with lambda
                                  reply_handler=lambda: d.callback(True),
                                  error_handler=d.errback)

        self.device.ChangePin(good_pin, bad_pin,
                              dbus_interface=CRD_INTFACE,
                              reply_handler=pin_changed_cb,
                              error_handler=d.errback)

        return d

    # if we unlocked the PIN at Enable we must increase the timeout
    # as the core gives the device 15 seconds to settle.
    test_CardChangePin.timeout = 30

    def test_CardCheck(self):
        """Test for Card.Check"""
        if not TEST_WADER_EXTENSIONS:
            raise unittest.SkipTest(GENERIC_SKIP_MSG)

        d = defer.Deferred()

        def card_check_cb(status):
            self.assertEqual(status, "READY")
            d.callback(True)

        self.device.Check(dbus_interface=CRD_INTFACE,
                          reply_handler=card_check_cb,
                          error_handler=d.errback)

        return d

    def test_CardEnableEcho(self):
        """Test for Card.EnableEcho"""
        # disabling Echo will probably leave Wader unusable
        raise unittest.SkipTest("Untestable method")

    def test_CardEnablePin(self):
        """Test for Card.EnablePin"""
        d = defer.Deferred()
        pin = config.get('test', 'pin', '0000')

        def disable_pin_cb():
            # now enable it again
            self.device.EnablePin(pin, True,
                                  dbus_interface=CRD_INTFACE,
                                  # test finishes with lambda
                                  reply_handler=lambda: d.callback(True),
                                  error_handler=d.errback)
        # disable PIN auth
        self.device.EnablePin(pin, False,
                              dbus_interface=CRD_INTFACE,
                              reply_handler=disable_pin_cb,
                              error_handler=d.errback)
        return d

    test_CardEnablePin.timeout = 15

    def test_CardGetCharset(self):
        """Test for Card.GetCharset"""
        d = defer.Deferred()

        def get_charset_cb(charset):
            self.failUnlessIn(charset, ['GSM', 'IRA', 'UCS2'])
            d.callback(True)

        self.device.GetCharset(dbus_interface=CRD_INTFACE,
                               reply_handler=get_charset_cb,
                               error_handler=d.errback)
        return d

    def test_CardGetCharsets(self):
        """Test for Card.GetCharsets"""
        d = defer.Deferred()

        def get_charsets_cb(charsets):
            self.failUnlessIn('IRA', charsets)
            self.failUnlessIn('UCS2', charsets)
            d.callback(True)

        self.device.GetCharsets(dbus_interface=CRD_INTFACE,
                                reply_handler=get_charsets_cb,
                                error_handler=d.errback)
        return d

    def test_CardGetImei(self):
        """Test for Card.GetImei"""
        d = defer.Deferred()

        def get_imei_cb(imei):
            imei_regexp = re.compile('^\d{14,17}$') # 14 <= IMEI <= 17
            self.failUnless(imei_regexp.match(imei))
            d.callback(True)

        self.device.GetImei(dbus_interface=CRD_INTFACE,
                            reply_handler=get_imei_cb,
                            error_handler=d.errback)
        return d

    def test_CardGetImsi(self):
        """Test for Card.GetImsi"""
        d = defer.Deferred()

        def get_imsi_cb(imsi):
            # according to http://en.wikipedia.org/wiki/IMSI there are
            # also IMSIs with 14 digits
            imsi_regexp = re.compile('^\d{14,15}$') # 14 <= IMSI <= 15
            self.failUnless(imsi_regexp.match(imsi))
            d.callback(True)

        self.device.GetImsi(dbus_interface=CRD_INTFACE,
                            reply_handler=get_imsi_cb,
                            error_handler=d.errback)
        return d

    def test_CardResetSettings(self):
        """Test for Card.ResetSettings"""
        if not TEST_WADER_EXTENSIONS:
            raise unittest.SkipTest(GENERIC_SKIP_MSG)

        raise unittest.SkipTest("Untested")

    def test_CardSendATString(self):
        """Test for Card.SendATString"""
        if not TEST_WADER_EXTENSIONS:
            raise unittest.SkipTest(GENERIC_SKIP_MSG)

        raise unittest.SkipTest("Untested")

    def test_CardSendPin(self):
        """Test for Card.SendPin"""
        raise unittest.SkipTest("Untested")

    def test_CardSendPuk(self):
        """Test for Card.SendPuk"""
        raise unittest.SkipTest("Untested")

    def test_CardSetCharset(self):
        """Test for Card.SetCharset"""
        d = defer.Deferred()
        charsets = ["IRA", "GSM", "UCS2"]

        def get_charset_cb(charset):
            self.failUnlessIn(charset, charsets)
            # now pick a new charset
            new_charset = ""
            while True:
                new_charset = random.choice(charsets)
                if new_charset != charset:
                    break

            def get_charset2_cb(_charset):
                # check that the new charset is the expected one
                self.assertEqual(new_charset, _charset)
                # leave everything as found
                self.device.SetCharset(charset,
                                       dbus_interface=CRD_INTFACE,
                                       # test finishes with lambda
                                       reply_handler=lambda: d.callback(True),
                                       error_handler=d.errback)

            # set the charset to new_charset
            self.device.SetCharset(new_charset,
                                   dbus_interface=CRD_INTFACE,
                                   error_handler=d.errback,
                                   reply_handler=lambda:
                                       self.device.GetCharset(
                                           dbus_interface=CRD_INTFACE,
                                           reply_handler=get_charset2_cb,
                                           error_handler=d.errback))

        # get the current charset
        self.device.GetCharset(dbus_interface=CRD_INTFACE,
                               reply_handler=get_charset_cb,
                               error_handler=d.errback)
        return d

    def test_CardSupportedBandsProperty(self):
        """Test for Card.SupportedBands property"""
        bands = self.device.Get(CRD_INTFACE, 'SupportedBands',
                                dbus_interface=dbus.PROPERTIES_IFACE)
        if not bands:
            raise unittest.SkipTest("Cannot be tested")

        self.failIfIn(MM_NETWORK_BAND_ANY, get_bands(bands))

    def test_CardSupportedModesProperty(self):
        """Test for Card.SupportedModes property"""
        modes = self.device.Get(CRD_INTFACE, 'SupportedModes',
                                dbus_interface=dbus.PROPERTIES_IFACE)
        if not modes:
            raise unittest.SkipTest("Cannot be tested")

        self.failUnlessIn(MM_NETWORK_MODE_ANY, modes)

    # org.freedesktop.ModemManager.Modem.Gsm.Contacts tests
    def test_ContactsAdd(self):
        """Test for Contacts.Add"""
        d = defer.Deferred()
        name, number = "John", "+435443434343"

        def add_contact_cb(index):

            def on_contact_fetched((_index, _name, _number)):
                self.assertEqual(name, _name)
                self.assertEqual(number, _number)
                # leave everything as found
                self.device.Delete(_index, dbus_interface=CTS_INTFACE,
                                   # test finishes with lambda
                                   reply_handler=lambda: d.callback(True),
                                   error_handler=d.errback)

            # get the object via DBus and check that its data is correct
            self.device.Get(index, dbus_interface=CTS_INTFACE,
                            reply_handler=on_contact_fetched,
                            error_handler=d.errback)

        self.device.Add(name, number,
                        dbus_interface=CTS_INTFACE,
                        reply_handler=add_contact_cb,
                        error_handler=d.errback)
        return d

    def test_ContactsAdd_UTF8_name(self):
        """Test for Contacts.Add"""
        d = defer.Deferred()
        name, number = u"中华人民共和国", "+43544311113"

        def add_contact_cb(index):

            def on_contact_fetched((_index, _name, _number)):
                self.assertEqual(name, _name)
                self.assertEqual(number, _number)
                # leave everything as found
                self.device.Delete(_index, dbus_interface=CTS_INTFACE,
                                   # test finishes with lambda
                                   reply_handler=lambda: d.callback(True),
                                   error_handler=d.errback)

            # get the object via DBus and check that its data is correct
            self.device.Get(index, dbus_interface=CTS_INTFACE,
                            reply_handler=on_contact_fetched,
                            error_handler=d.errback)

        self.device.Add(name, number,
                        dbus_interface=CTS_INTFACE,
                        reply_handler=add_contact_cb,
                        error_handler=d.errback)
        return d

    def test_ContactsDelete(self):
        """Test for Contacts.Delete"""
        d = defer.Deferred()
        name, number = "Juan", "+21544343434"

        def on_contact_added(index):

            def is_it_present(contacts):
                self.assertNotIn(index, [c[0] for c in contacts])
                d.callback(True)

            # now delete it and check that its index is no longer present
            # if we list all the contacts
            self.device.Delete(index, dbus_interface=CTS_INTFACE,
                               error_handler=d.errback,
                               reply_handler=lambda:
                                  self.device.List(dbus_interface=CTS_INTFACE,
                                                   reply_handler=is_it_present,
                                                   error_handler=d.errback))

        # add a contact, and delete it
        self.device.Add(name, number, dbus_interface=CTS_INTFACE,
                        reply_handler=on_contact_added,
                        error_handler=d.errback)
        return d

    def test_ContactsEdit(self):
        """Test for Contacts.Edit"""
        d = defer.Deferred()
        name, number = "Eugenio", "+435345342121"
        new_name, new_number = "Eugenia", "+43542323122"

        def add_contact_cb(index):

            def get_contact_cb((_index, _name, _number)):
                self.assertEqual(_name, new_name)
                self.assertEqual(_number, new_number)
                # leave everything as found
                self.device.Delete(_index, dbus_interface=CTS_INTFACE,
                                   # test finishes with lambda
                                   reply_handler=lambda: d.callback(True),
                                   error_handler=d.errback)

            # edit it and get by index to check that the new values are set
            self.device.Edit(index, new_name, new_number,
                             dbus_interface=CTS_INTFACE,
                             error_handler=d.errback,
                             reply_handler=lambda index:
                                self.device.Get(index,
                                                dbus_interface=CTS_INTFACE,
                                                reply_handler=get_contact_cb,
                                                error_handler=d.errback))
        # add a contact
        self.device.Add(name, number,
                        dbus_interface=CTS_INTFACE,
                        reply_handler=add_contact_cb,
                        error_handler=d.errback)
        return d

    def test_ContactsFindByName(self):
        """Test for Contacts.FindByName"""
        test_data = {
            'JuanFoo' : [0, '666066660'],
            'JuanBar' : [0, '666066661'],
            'JuanBaz' : [0, '666166662'],
        }
        test_searches = [
            ('JuanB', 2), ('Jua', 3), ('JuanFoo', 1), ('Stuff', 0)
        ]

        for name, datat in test_data.iteritems():
            test_data[name][0] = self.device.Add(name, datat[1],
                                                dbus_interface=CTS_INTFACE)
        for current_search in test_searches:
            result_list = self.device.FindByName(current_search[0],
                                                 dbus_interface=CTS_INTFACE)

            self.assertEqual(len(result_list), current_search[1])
            if current_search[1] != 0:
                for result in result_list:
                    self.assertEqual(result[2], test_data[result[1]][1])

        for name, datat in test_data.iteritems():
            self.device.Delete(datat[0], dbus_interface=CTS_INTFACE)

    def test_ContactsFindByNumber(self):
        """Test for Contacts.FindByNumber"""
        test_data = {
            '666066660' : [0, 'JuanFoo'],
            '666066661' : [0, 'JuanBar'],
            '666166662' : [0, 'JuanBaz'],
        }
        test_searches = [
            ('6660', 2), ('666', 3), ('666066660', 1), ('1234', 0),
        ]

        for number, datat in test_data.iteritems():
            test_data[number][0] = self.device.Add(datat[1], number,
                                                   dbus_interface=CTS_INTFACE)

        for current_search in test_searches:
            result_list = self.device.FindByNumber(current_search[0],
                                                   dbus_interface=CTS_INTFACE)
            self.assertEqual(len(result_list), current_search[1])

            if current_search[1] != 0:
                for result in result_list:
                    self.assertEqual(result[1], test_data[result[2]][1])

        for number, datat in test_data.iteritems():
            self.device.Delete(datat[0], dbus_interface=CTS_INTFACE)

    def test_ContactsGet(self):
        """Test Contacts.Get"""
        d = defer.Deferred()
        name, number = "Mario", "+312232332"

        def add_contact_cb(index):

            def get_contact_cb(reply):
                self.assertIn(name, reply)
                self.assertIn(number, reply)
                self.assertIn(index, reply)

                # leave everything as found
                self.device.Delete(index,
                                   dbus_interface=CTS_INTFACE,
                                   # test finishes with lambda
                                   reply_handler=lambda: d.callback(True),
                                   error_handler=d.errback)

            # test get by index
            self.device.Get(index,
                            dbus_interface=CTS_INTFACE,
                            reply_handler=get_contact_cb,
                            error_handler=d.errback)
        # add a contact
        self.device.Add(name, number,
                        dbus_interface=CTS_INTFACE,
                        reply_handler=add_contact_cb,
                        error_handler=d.errback)
        return d

    def test_ContactsGetCount(self):
        """Test for Contacts.GetCount"""
        d = defer.Deferred()

        def get_count_cb(count):

            def list_contacts_cb(contacts):
                # this two should match
                self.assertEqual(count, len(contacts))
                d.callback(True)

            self.device.List(dbus_interface=CTS_INTFACE,
                             reply_handler=list_contacts_cb,
                             error_handler=d.errback)

        # get the total count and compare it
        self.device.GetCount(dbus_interface=CTS_INTFACE,
                             reply_handler=get_count_cb,
                             error_handler=d.errback)
        return d

    def test_ContactsGetCount_2(self):
        """Test for Contacts.GetCount"""
        count = self.device.GetCount(dbus_interface=CTS_INTFACE)
        index = self.device.Add("Boethius", "+21123322323",
                                dbus_interface=CTS_INTFACE)
        count2 = self.device.GetCount(dbus_interface=CTS_INTFACE)
        self.assertEqual(count + 1, count2)
        self.device.Delete(index, dbus_interface=CTS_INTFACE)

    def test_ContactsGetPhonebookSize(self):
        """Test for Contacts.GetPhonebookSize"""
        d = defer.Deferred()

        def get_phonebooksize_cb(size):
            self.failUnlessIsInstance(size, int)
            self.failUnless(size >= 200)
            d.callback(True)

        self.device.GetPhonebookSize(dbus_interface=CTS_INTFACE,
                                     reply_handler=get_phonebooksize_cb,
                                     error_handler=d.errback)
        return d

    def test_ContactsList(self):
        """Test for Contacts.List"""
        d = defer.Deferred()
        name, number = "Jauma", "+356456445654"

        def add_contact_cb(index):

            def list_contacts_cb(reply):
                found = False
                for contact in reply:
                    if (index, name, number) == contact:
                        found = True
                        break

                # check that we found it
                self.failUnless(found)

                # leave everything as found
                self.device.Delete(index,
                                   dbus_interface=CTS_INTFACE,
                                   # test finishes with lambda
                                   reply_handler=lambda: d.callback(True),
                                   error_handler=d.errback)

            self.device.List(dbus_interface=CTS_INTFACE,
                             reply_handler=list_contacts_cb,
                             error_handler=d.errback)

        self.device.Add(name, number,
                        dbus_interface=CTS_INTFACE,
                        reply_handler=add_contact_cb,
                        error_handler=d.errback)
        return d

    def test_ContactsList_2(self):
        """Test for Contacts.List"""
        contacts = [
                {'name' : "FooAnt" , 'number' : "+34666666666" , 'index' : 0},
                {'name' : "BarAnt" , 'number' : "+34666666665" , 'index' : 0},
                {'name' : "BazAnt" , 'number' : "+34666666664" , 'index' : 0}
                ]

        for contact in contacts:
            contact['index'] = self.device.Add(contact['name'],
                                               contact['number'])

        for contact in contacts:
            self.assertEqual(self.device.FindByNumber(contact['number'])[0][1],
                                                      contact['name'] )

        for contact in contacts:
            self.device.Delete(contact['index'])

    # org.freedesktop.ModemManager.Modem.Gsm.Network tests
    def test_NetworkGetApns(self):
        """Test for Network.GetApns"""
        if not TEST_WADER_EXTENSIONS:
            raise unittest.SkipTest(GENERIC_SKIP_MSG)

        raise unittest.SkipTest("Untested")

    def test_NetworkGetBand(self):
        """Test for Network.GetBand"""
        d = defer.Deferred()

        def get_band_cb(band):
            self.failUnlessIsInstance(band, (dbus.UInt32, int))
            self.failUnless(band > 0)
            d.callback(True)

        self.device.GetBand(dbus_interface=NET_INTFACE,
                            reply_handler=get_band_cb,
                            error_handler=d.errback)
        return d

    def test_NetworkGetNetworkMode(self):
        """Test for Network.GetNetworkMode"""
        d = defer.Deferred()

        def get_network_mode_cb(mode):
            self.failUnlessIsInstance(mode, (dbus.UInt32, int))
            # currently goes between 0 and 12
            self.failUnless(mode >= 0 and mode < 20)
            d.callback(True)

        self.device.GetNetworkMode(dbus_interface=NET_INTFACE,
                                   reply_handler=get_network_mode_cb,
                                   error_handler=d.errback)
        return d

    def test_NetworkGetRegistrationInfo(self):
        """Test for Network.GetRegistrationInfo"""
        d = defer.Deferred()

        def get_registration_info_cb(reply):
            status, numeric_oper = reply[:2]
            # we must be registered to our home network or roaming
            self.failUnlessIn(status, [1, 5])

            def check_numeric_oper_too(imsi):
                # we should be registered with our home network
                self.failUnless(imsi.startswith(numeric_oper))
                d.callback(True)

            # get the IMSI and check that we are connected to a network
            # with a netid that matches the beginning of our IMSI
            self.device.GetImsi(dbus_interface=CRD_INTFACE,
                                reply_handler=check_numeric_oper_too,
                                error_handler=d.errback)

        self.device.GetRegistrationInfo(dbus_interface=NET_INTFACE,
                                        reply_handler=get_registration_info_cb,
                                        error_handler=d.errback)
        return d

    def test_NetworkGetRoamingIDs(self):
        """Test for Network.GetRoamingIDs"""
        if not TEST_WADER_EXTENSIONS:
            raise unittest.SkipTest(GENERIC_SKIP_MSG)

        raise unittest.SkipTest("This method is device-dependent")

    def test_NetworkGetSignalQuality(self):
        """Test for Network.GetSignalQuality"""
        d = defer.Deferred()

        def get_signal_quality_cb(quality):
            # signal quality should be an int between 1 and 100
            self.failUnlessIsInstance(quality, (dbus.UInt32, int))
            self.failUnless(quality >= 1 and quality <= 100)
            d.callback(True)

        self.device.GetSignalQuality(dbus_interface=NET_INTFACE,
                                     reply_handler=get_signal_quality_cb,
                                     error_handler=d.errback)
        return d

    def test_NetworkScan(self):
        """Test for Network.Scan"""
        d = defer.Deferred()

        def get_imsi_cb(imsi):

            def network_scan_cb(networks):
                home_network_found = False
                for network in networks:
                    if network['operator-num'] == imsi[:5]:
                        home_network_found = True
                        break

                # our home network has to be around
                # unless we are roaming ;)
                self.assertEqual(home_network_found, True)
                d.callback(True)

            self.device.Scan(dbus_interface=NET_INTFACE,
                             # increase the timeout as Scan is a
                             # potentially long operation
                             timeout=45,
                             reply_handler=network_scan_cb,
                             error_handler=d.errback)

        # get the first five digits of the IMSI and check that its around
        self.device.GetImsi(dbus_interface=CRD_INTFACE,
                            reply_handler=get_imsi_cb,
                            error_handler=d.errback)
        return d

    def test_NetworkSetApn(self):
        """Test for Network.SetApn"""
        raise unittest.SkipTest("Untested")

    def test_NetworkSetBand(self):
        """Test for Network.SetBand"""
        _bands = self.device.Get(CRD_INTFACE, 'SupportedBands',
                                dbus_interface=dbus.PROPERTIES_IFACE)
        if not _bands:
            raise unittest.SkipTest("Cannot be tested")

        bands = get_bands(_bands)

        while bands:
            band = bands.pop()
            self.device.SetBand(band,
                                dbus_interface=NET_INTFACE)
            _band = self.device.GetBand(dbus_interface=NET_INTFACE)
            self.failUnless(band & _band)

        # leave it in BAND_ANY
        self.device.SetBand(MM_NETWORK_BAND_ANY)
        time.sleep(5)

    def test_NetworkSetNetworkMode(self):
        """Test for Network.SetNetworkMode"""
        modes = self.device.Get(CRD_INTFACE, 'SupportedModes',
                                dbus_interface=dbus.PROPERTIES_IFACE)
        if not modes:
            raise unittest.SkipTest("Cannot be tested")

        while modes:
            mode = modes.pop()
            self.device.SetNetworkMode(mode,
                                       dbus_interface=NET_INTFACE)
            _mode = self.device.GetNetworkMode(dbus_interface=NET_INTFACE)
            self.assertEqual(mode, _mode)

        # leave it in MODE_ANY
        self.device.SetNetworkMode(MM_NETWORK_MODE_ANY,
                                   dbus_interface=NET_INTFACE)
        time.sleep(5)

    def test_NetworkSetRegistrationNotification(self):
        """Test for Network.SetRegistrationNotification"""
        raise unittest.SkipTest("Untested")

    def test_NetworkSetInfoFormat(self):
        """Test for Network.SetInfoFormat"""
        raise unittest.SkipTest("Untested")

    def test_NetworkRegister(self):
        """Test for Network.Register"""
        raise unittest.SkipTest("Untested")

    # org.freedesktop.ModemManager.Modem.Gsm.Simple tests
    def test_SimpleConnect(self):
        """Test for Simple.Connect"""
        raise unittest.SkipTest("Untested")

    def test_SimpleDisconnect(self):
        """Test for Simple.Disconnect"""
        raise unittest.SkipTest("Untested")

    def test_SimpleGetStatus(self):
        """Test for Simple.GetStatus"""
        d = defer.Deferred()

        def get_status_cb(status):
            self.failUnless('band' in status)
            self.failUnless('signal_quality' in status)
            self.failUnless('operator_code' in status)
            self.failUnless('operator_name' in status)
            self.failUnlessIsInstance(status['operator_name'], basestring)
            self.failUnlessIsInstance(status['operator_code'], basestring)
            self.failUnlessIsInstance(status['signal_quality'], dbus.UInt32)
            self.failUnlessIsInstance(status['band'], dbus.UInt32)

            d.callback(True)

        self.device.GetStatus(dbus_interface=SPL_INTFACE,
                              reply_handler=get_status_cb,
                              error_handler=d.errback)
        return d

    # org.freedesktop.ModemManager.Modem.Gsm.SMS tests
    def test_SmsDelete(self):
        """Test for SMS.Delete"""
        d = defer.Deferred()
        sms = {'number' : '+33622754135', 'text' : 'delete test'}

        def sms_saved_cb(indexes):

            def on_sms_list_cb(messages):
                sms_found = False
                for msg in messages:
                    if msg['index'] == indexes[0]:
                        sms_found = True

                # the index should not be present
                self.assertEqual(sms_found, False)
                d.callback(True)

            self.assertEqual(len(indexes), 1)
            self.device.Delete(indexes[0], dbus_interface=SMS_INTFACE,
                               error_handler=d.errback,
                               reply_handler=lambda:
                                   self.device.List(
                                       dbus_interface=SMS_INTFACE,
                                       reply_handler=on_sms_list_cb,
                                       error_handler=d.errback))

        # save a sms, delete it and check is no longer present
        self.device.Save(sms, dbus_interface=SMS_INTFACE,
                         reply_handler=sms_saved_cb,
                         error_handler=d.errback)
        return d

    def test_SmsDeleteMultiparted(self):
        """Test for SMS.Delete"""
        d = defer.Deferred()
        sms = {'number' : '+34622754135',
               'text' : """test_SmsDeleteMultiparted test_SmsDeleteMultiparted
                           test_SmsDeleteMultiparted test_SmsDeleteMultiparted
                           test_SmsDeleteMultiparted test_SmsDeleteMultiparted
                           test_SmsDeleteMultiparted test_SmsDeleteMultiparted
                           """
        }

        def sms_saved_cb(indexes):

            def on_sms_list_cb(messages):
                sms_found = False
                for msg in messages:
                    if msg['index'] == indexes[0]:
                        sms_found = True

                # the index should not be present
                self.assertEqual(sms_found, False)
                d.callback(True)

            self.assertEqual(len(indexes), 1)
            self.device.Delete(indexes[0], dbus_interface=SMS_INTFACE,
                               error_handler=d.errback,
                               reply_handler=lambda:
                                   self.device.List(
                                       dbus_interface=SMS_INTFACE,
                                       reply_handler=on_sms_list_cb,
                                       error_handler=d.errback))

        # save a sms, delete it and check is no longer present
        self.device.Save(sms, dbus_interface=SMS_INTFACE,
                         reply_handler=sms_saved_cb,
                         error_handler=d.errback)
        return d

    def test_SmsGet(self):
        """Test for SMS.Get"""
        d = defer.Deferred()
        sms = {'number' : '+33646754145', 'text' : 'get test'}

        def sms_get_cb(_sms):
            self.assertEqual(sms['number'], _sms['number'])
            self.assertEqual(sms['text'], _sms['text'])
            # leave everything as found
            self.device.Delete(_sms['index'], dbus_interface=SMS_INTFACE,
                               reply_handler=lambda: d.callback(True),
                               error_handler=d.errback)

        # save the message, get it by index, and check its values match
        self.device.Save(sms, dbus_interface=SMS_INTFACE,
                         error_handler=d.errback,
                         reply_handler=lambda indexes:
                             self.device.Get(indexes[0],
                                         dbus_interface=SMS_INTFACE,
                                         reply_handler=sms_get_cb,
                                         error_handler=d.errback))
        return d

    def test_SmsGetMultiparted(self):
        """Test for SMS.Get"""
        d = defer.Deferred()

        sms = {'number' : '+34622754135',
               'text' : """test_SmsGetMultiparted test_SmsGetMultiparted
                           test_SmsGetMultiparted test_SmsGetMultiparted
                           test_SmsGetMultiparted test_SmsGetMultiparted
                           test_SmsGetMultiparted test_SmsGetMultiparted
                           """
        }

        def sms_get_cb(_sms):
            self.assertEqual(sms['number'], _sms['number'])
            self.assertEqual(sms['text'], _sms['text'])
            # leave everything as found
            self.device.Delete(_sms['index'], dbus_interface=SMS_INTFACE,
                               reply_handler=lambda: d.callback(True),
                               error_handler=d.errback)

        # save the message, get it by index, and check its values match
        self.device.Save(sms, dbus_interface=SMS_INTFACE,
                         error_handler=d.errback,
                         reply_handler=lambda indexes:
                             self.device.Get(indexes[0],
                                         dbus_interface=SMS_INTFACE,
                                         reply_handler=sms_get_cb,
                                         error_handler=d.errback))
        return d

    def test_SmsGetSmsc(self):
        """Test for SMS.GetSmsc"""
        d = defer.Deferred()

        def get_smsc_cb(smsc):
            self.failUnless(smsc.startswith('+'))
            d.callback(True)

        self.device.GetSmsc(dbus_interface=SMS_INTFACE,
                            reply_handler=get_smsc_cb,
                            error_handler=d.errback)
        return d

    def test_SmsGetFormat(self):
        """Test for SMS.GetFormat"""
        d = defer.Deferred()

        def get_format_cb(fmt):
            self.failUnlessIn(fmt, [0, 1])
            d.callback(True)

        self.device.GetFormat(dbus_interface=SMS_INTFACE,
                              reply_handler=get_format_cb,
                              error_handler=d.errback)
        return d

    def test_SmsList(self):
        """Test for SMS.List"""
        d = defer.Deferred()
        sms = {'number' : '+33622754135', 'text' : 'list test'}

        def sms_saved_cb(indexes):
            # now check that the indexes are present in a List
            def sms_list_cb(messages):
                sms_found = False

                for msg in messages:
                    if msg['index'] == indexes[0]:
                        sms_found = True
                        break

                self.assertEqual(sms_found, True)

                # leave everything as found
                self.device.Delete(indexes[0],
                                   dbus_interface=SMS_INTFACE,
                                   reply_handler=lambda: d.callback(True),
                                   error_handler=d.errback)

            self.device.List(dbus_interface=SMS_INTFACE,
                             reply_handler=sms_list_cb,
                             error_handler=d.errback)

        self.device.Save(sms, dbus_interface=SMS_INTFACE,
                         reply_handler=sms_saved_cb,
                         error_handler=d.errback)
        return d

    def test_SmsList_2(self):
        # get the current number of Sms
        size_before = len(self.device.List(dbus_interface=SMS_INTFACE))

        # add three new ones
        indexes = []
        what = [
            {'number':'+324342322', 'text': 'hey there'},
            {'number':'+334223312', 'text': 'where you at?'},
            {'number':'+324323232', 'text': 'hows it going?'}
        ]

        for sms in what:
            indexes.extend(self.device.Save(sms, dbus_interface=SMS_INTFACE))

        size_after = len(self.device.List(dbus_interface=SMS_INTFACE))
        # and check that the size has increased just three
        self.assertEqual(size_before + 3, size_after)

        # leave everything as found
        for index in indexes:
            self.device.Delete(index, dbus_interface=SMS_INTFACE)

    def test_SmsListMultiparted(self):
        """Test for SMS.List"""
        d = defer.Deferred()
        sms = {'number' : '+34622754135',
                'text' : """test_SmsListMultiparted test_SmsListMultiparted
                            test_SmsListMultiparted test_SmsListMultiparted
                            test_SmsListMultiparted test_SmsListMultiparted
                            test_SmsListMultiparted test_SmsListMultiparted
                            """
        }

        def sms_saved_cb(indexes):
            # now check that the indexes are present in a List
            def sms_list_cb(messages):
                sms_found = False

                for msg in messages:
                    if msg['index'] == indexes[0]:
                        sms_found = True
                        break

                self.assertEqual(sms_found, True)

                # leave everything as found
                self.device.Delete(indexes[0],
                                   dbus_interface=SMS_INTFACE,
                                   reply_handler=lambda: d.callback(True),
                                   error_handler=d.errback)

            self.device.List(dbus_interface=SMS_INTFACE,
                             reply_handler=sms_list_cb,
                             error_handler=d.errback)

        self.device.Save(sms, dbus_interface=SMS_INTFACE,
                         reply_handler=sms_saved_cb,
                         error_handler=d.errback)
        return d

    def test_SmsListMultiparted_2(self):
        # get the current number of Sms
        size_before = len(self.device.List(dbus_interface=SMS_INTFACE))
        # add three new ones
        what = [
            {'number' : '+324342322', 'text': 'hey there'},
            {'number' : '+34622754135',
             'text' : """test_SmsListMultiparted_2 test_SmsListMultiparted_2
                         test_SmsListMultiparted_2 test_SmsListMultiparted_2
                         test_SmsListMultiparted_2 test_SmsListMultiparted_2
                         test_SmsListMultiparted_2 test_SmsListMultiparted_2
                         """},
            {'number' : '+34622754135',
             'text' : """test_SmsListMultiparted_2 test_SmsListMultiparted_2
                         test_SmsListMultiparted_2 test_SmsListMultiparted_2
                         test_SmsListMultiparted_2 test_SmsListMultiparted_2
                         test_SmsListMultiparted_2 test_SmsListMultiparted_2
                          """},
            {'number':'+324323232', 'text': 'hows it going?'},
        ]

        indexes = []
        for sms in what:
            indexes.extend(self.device.Save(sms, dbus_interface=SMS_INTFACE))

        size_after = len(self.device.List(dbus_interface=SMS_INTFACE))
        # and check that the size has increased just three
        self.assertEqual(size_before + 4, size_after)

        # leave everything as found
        for index in indexes:
            self.device.Delete(index, dbus_interface=SMS_INTFACE)

    def test_SmsSave(self):
        """Test for SMS.Save"""
        d = defer.Deferred()
        sms = {'number' : '+34645454445', 'text' : 'save test'}

        def sms_get_cb(_sms):
            self.assertEqual(sms['number'], _sms['number'])
            self.assertEqual(sms['text'], _sms['text'])
            # leave everything as found
            self.device.Delete(_sms['index'], dbus_interface=SMS_INTFACE,
                               # test finishes with lambda
                               reply_handler=lambda: d.callback(True),
                               error_handler=d.errback)

        # save the message, get it by index, and check its values match
        self.device.Save(sms, dbus_interface=SMS_INTFACE,
                         error_handler=d.errback,
                         reply_handler=lambda indexes:
                            self.device.Get(indexes[0],
                                dbus_interface=SMS_INTFACE,
                                reply_handler=sms_get_cb,
                                error_handler=d.errback))

        return d

    def test_SmsSaveMultiparted(self):
        """Test for SMS.Save"""
        d = defer.Deferred()
        sms = {'number' : '+34622754135',
               'text' : """test_SmsSaveMultiparted test_SmsSaveMultiparted
                           test_SmsSaveMultiparted test_SmsSaveMultiparted
                           test_SmsSaveMultiparted test_SmsSaveMultiparted
                           test_SmsSaveMultiparted test_SmsSaveMultiparted
                           """
        }

        def sms_get_cb(_sms):
            self.assertEqual(sms['number'], _sms['number'])
            self.assertEqual(sms['text'], _sms['text'])
            # leave everything as found
            self.device.Delete(_sms['index'], dbus_interface=SMS_INTFACE,
                               # test finishes with lambda
                               reply_handler=lambda: d.callback(True),
                               error_handler=d.errback)

        # save the message, get it by index, and check its values match
        self.device.Save(sms, dbus_interface=SMS_INTFACE,
                         error_handler=d.errback,
                         reply_handler=lambda indexes:
                            self.device.Get(indexes[0],
                                dbus_interface=SMS_INTFACE,
                                reply_handler=sms_get_cb,
                                error_handler=d.errback))

        return d

    def test_SmsSend(self):
        """Test for SMS.Send"""
        raise unittest.SkipTest("Not ready")
        #number = config.get('test', 'phone')
        #if not number:
        #    raise unittest.SkipTest("Cannot run this test without a number")

        #d = defer.Deferred()
        #sm = None  # SignalMatch
        #sms = {'number' : number, 'text' : 'send test'}

        #def on_sms_received_cb(index):
        #    def compare_messages(_sms):
        #        self.assertEqual(_sms['text'], sms['text'])
        #        sm.remove() # remove SignalMatch
        #        # leave everything as found
        #        self.device.Delete(index, dbus_interface=SMS_INTFACE,
        #                           reply_handler=lambda: d.callback(True),
        #                           error_handler=d.errback)

        #    self.device.Get(index, dbus_interface=SMS_INTFACE,
        #                    reply_handler=compare_messages,
        #                    error_handler=d.errback)

        #sm = self.device.connect_to_signal("SMSReceived", on_sms_received_cb,
        #                                   dbus_interface=SMS_INTFACE)

        #self.device.Send(sms, dbus_interface=SMS_INTFACE,
        #                 # we are not interested in the callback
        #                 reply_handler=lambda indexes: None,
        #                 error_handler=d.errback)

        #return d

    def test_SmsSendFromStorage(self):
        """Test for SMS.SendFromStorage"""
        raise unittest.SkipTest("Not ready")
        #number = config.get('test', 'phone')
        #if not number:
        #    raise unittest.SkipTest("Cannot run this test without a number")
        #d = defer.Deferred()
        #sm = None  # SignalMatch
        #sms = {'number' : number, 'text' : 'send from storage test' }

        #def on_sms_received_cb(index):
        #    def compare_messages(_sms):
        #        self.assertEqual(_sms['text'], sms['text'])
        #        sm.remove() # remove SignalMatch
        #        # leave everything as found
        #        self.device.Delete(index, dbus_interface=SMS_INTFACE,
        #                           reply_handler=lambda: d.callback(True),
        #                           error_handler=d.errback)

        #    # now get it by index and check text is the same
        #    self.device.Get(index, dbus_interface=SMS_INTFACE,
        #                    reply_handler=compare_messages,
        #                    error_handler=d.errback)

        #def on_sms_saved_cb(indexes):
        #    self.assertEqual(len(indexes), 1)

        #    # send it from storage and wait for the signal
        #    self.device.SendFromStorage(indexes[0],
        #                                dbus_interface=SMS_INTFACE,
        #                                # we are not interested in the callback
        #                                reply_handler=lambda indexes: None,
        #                                error_handler=d.errback)

        #sm = self.device.connect_to_signal("SMSReceived", on_sms_received_cb)

        ## save the message and send it to ourselves
        #self.device.Save(sms, dbus_interface=SMS_INTFACE,
        #                 reply_handler=on_sms_saved_cb,
        #                 error_handler=d.errback)

        #return d

    def test_SmsSetFormat(self):
        """Test for SMS.SetFormat"""
        d = defer.Deferred()

        def get_format_cb(fmt):
            self.assertEquals(fmt, 1)
            # leave format as found
            self.device.SetFormat(0,
                                  dbus_interface=SMS_INTFACE,
                                  # test finishes with lambda
                                  reply_handler=lambda: d.callback(True),
                                  error_handler=d.errback)

        def set_format_eb(e):
            if 'CMSError303' in get_dbus_error(e):
                # it does not support setting +CMFG=1 (Ericsson)
                d.callback(True)
            else:
                d.errback(e)

        # set text format and check immediately that a
        # GetFormat call returns 1
        self.device.SetFormat(1, dbus_interface=SMS_INTFACE,
                              error_handler=set_format_eb,
                              reply_handler=lambda:
                                    self.device.GetFormat(
                                      dbus_interface=SMS_INTFACE,
                                      reply_handler=get_format_cb,
                                      error_handler=d.errback))
        return d

    def test_SmsSetIndication(self):
        """Test for SMS.SetIndication"""
        raise unittest.SkipTest("Untested")

    def test_SmsSetSmsc(self):
        """Test for SMS.SetSmsc"""
        d = defer.Deferred()
        bad_smsc = '+3453456343'

        def get_smsc_cb(smsc):

            def get_bad_smsc_cb(_bad_smsc):
                # bad_smsc has been correctly set
                self.assertEqual(bad_smsc, _bad_smsc)
                # leave everything as found
                self.device.SetSmsc(smsc, dbus_interface=SMS_INTFACE,
                                    # test finishes with lambda
                                    reply_handler=lambda: d.callback(True),
                                    error_handler=d.errback)

            # set the SMSC to a bad value and read it to confirm it worked
            self.device.SetSmsc(bad_smsc, dbus_interface=SMS_INTFACE,
                                error_handler=d.errback,
                                reply_handler=lambda:
                                   self.device.GetSmsc(
                                       dbus_interface=SMS_INTFACE,
                                       reply_handler=get_bad_smsc_cb,
                                       error_handler=d.errback))

        # get the original SMSC and memoize it
        self.device.GetSmsc(dbus_interface=SMS_INTFACE,
                            reply_handler=get_smsc_cb,
                            error_handler=d.errback)
        return d
