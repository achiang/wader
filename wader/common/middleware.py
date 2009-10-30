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
"""
Wrapper around :class:`~wader.common.protocol.WCDMAProtocol`

It basically provides error control and more high-level operations.
N-tier folks can see this as a Business Logic class.
"""

from collections import deque

import serial
from twisted.python import log
from twisted.internet import defer, reactor

import wader.common.aterrors as E
from wader.common.consts import (CRD_INTFACE, MM_NETWORK_BAND_ANY,
                                 DEV_AUTHENTICATED, DEV_ENABLED, DEV_CONNECTED)
from wader.common.contact import Contact
from wader.common.encoding import (from_ucs2, from_u, unpack_ucs2_bytes,
                                   pack_ucs2_bytes, check_if_ucs2)
import wader.common.exceptions as ex
from wader.common.protocol import WCDMAProtocol
from wader.common.sim import RETRY_ATTEMPTS, RETRY_TIMEOUT
from wader.common.sms import Message, MessageAssemblyLayer


def regexp_to_contact(match):
    """
    Returns a :class:`wader.common.contact.Contact` out of ``match``

    :type match: ``re.MatchObject``
    """
    name = from_ucs2(match.group('name'))
    number = from_ucs2(match.group('number'))
    index = int(match.group('id'))
    return Contact(name, number, index=index)


class WCDMAWrapper(WCDMAProtocol):
    """
    I am a wrapper around :class:`~wader.common.protocol.WCDMAProtocol`

    Its main objective is to provide some error control on some operations
    and a cleaner API to deal with its results.
    """

    def __init__(self, device):
        super(WCDMAWrapper, self).__init__(device)
        # unfortunately some methods require me to save some state
        # between runs. This dict contains 'em.
        self.state_dict = {}
        # message assembly layer (initted on do_enable_device)
        self.mal = MessageAssemblyLayer(self)

    def __str__(self):
        return self.device.__remote_name__

    def add_contact(self, contact):
        """
        Adds ``contact`` to the SIM and returns the index where was stored
        """
        ucs2 = 'UCS2' in self.device.sim.charset
        name = pack_ucs2_bytes(contact.name) if ucs2 else from_u(contact.name)

        # common arguments for both operations (name and number)
        args = [name, from_u(contact.number)]

        if contact.index:
            # contact.index is set, user probably wants to overwrite an
            # existing contact
            args.append(contact.index)
            d = super(WCDMAWrapper, self).add_contact(*args)
            d.addCallback(lambda _: contact.index)
            return d

        def get_next_id_cb(index):
            args.append(index)
            d2 = super(WCDMAWrapper, self).add_contact(*args)
            # now we just fake add_contact's response and we return the index
            d2.addCallback(lambda _: index)
            return d2

        # contact.index is not set, this means that we need to obtain the
        # first free slot on the phonebook and then add the contact
        d = self._get_next_contact_id()
        d.addCallback(get_next_id_cb)
        return d

    def change_pin(self, oldpin, newpin):
        """Changes PIN from ``oldpin`` to ``newpin``"""
        d = super(WCDMAWrapper, self).change_pin(oldpin, newpin)
        d.addCallback(lambda result: result[0].group('resp'))
        return d

    def check_pin(self):
        """
        Returns the SIM's auth state

        :raise SimPinRequired: Raised if SIM PIN is required
        :raise SimPukRequired: Raised if SIM PUK is required
        :raise SimPuk2Required: Raised if SIM PUK2 is required
        """
        d = super(WCDMAWrapper, self).check_pin()

        def process_result(resp):
            result = resp[0].group('resp')
            if result == 'READY':
                return result
            elif result == 'SIM PIN':
                raise E.SimPinRequired()
            elif result == 'SIM PUK':
                raise E.SimPukRequired()
            elif result == 'SIM PUK2':
                raise E.SimPuk2Required()
            else:
                log.err("unknown authentication state %s" % result)

        d.addCallback(process_result)
        return d

    def delete_contact(self, index):
        """Deletes contact at ``index``"""
        d = super(WCDMAWrapper, self).delete_contact(index)
        d.addCallback(lambda result: result[0].group('resp'))
        return d

    def delete_sms(self, index):
        return self.mal.delete_sms(index)

    def do_delete_sms(self, index):
        """Deletes SMS at ``index``"""
        d = super(WCDMAWrapper, self).delete_sms(index)
        d.addCallback(lambda result: result[0].group('resp'))
        return d

    def disable_echo(self):
        """Disables echo"""
        d = super(WCDMAWrapper, self).disable_echo()
        d.addCallback(lambda result: result[0].group('resp'))
        return d

    def enable_pin(self, pin, enable):
        """
        Enables or disables PIN auth with ``pin`` according to ``enable``
        """

        def cache_and_return_response(response):
            self.device.props[CRD_INTFACE]['PinEnabled'] = enable
            return response[0].group('resp')

        d = super(WCDMAWrapper, self).enable_pin(pin, enable)
        d.addCallback(cache_and_return_response)
        return d

    def enable_echo(self):
        """
        Enables echo

        Use this with caution as it might leave Wader on an unusable state
        """
        d = super(WCDMAWrapper, self).enable_echo()
        d.addCallback(lambda result: result[0].group('resp'))
        return d

    def find_contacts(self, pattern):
        """
        Returns all the `Contact` objects whose name matches ``pattern``

        :rtype: list
        """
        if 'UCS2' in self.device.sim.charset:
            pattern = pack_ucs2_bytes(pattern)

        d = super(WCDMAWrapper, self).find_contacts(pattern)
        d.addCallback(lambda matches: map(regexp_to_contact, matches))
        return d

    def get_apns(self):
        """
        Returns all the APNs in the SIM

        :rtype: list
        """
        d = super(WCDMAWrapper, self).get_apns()
        d.addCallback(lambda resp:
                [(int(r.group('index')), r.group('apn')) for r in resp])
        return d

    def get_band(self):
        """Returns the current band used"""
        raise NotImplementedError()

    def get_bands(self):
        """
        Returns the available bands

        :rtype: list
        """
        bands = self.custom.band_dict.keys()
        if MM_NETWORK_BAND_ANY in bands:
            bands.pop(MM_NETWORK_BAND_ANY)

        return defer.succeed(sum(bands))

    def get_card_model(self):
        """Returns the card model"""
        d = super(WCDMAWrapper, self).get_card_model()
        d.addCallback(lambda response: response[0].group('model'))
        return d

    def get_card_version(self):
        """Returns the firmware version"""
        d = super(WCDMAWrapper, self).get_card_version()
        d.addCallback(lambda response: response[0].group('version'))
        return d

    def get_charset(self):
        """Returns the current charset"""
        d = super(WCDMAWrapper, self).get_charset()
        d.addCallback(lambda response: response[0].group('lang'))
        return d

    def get_charsets(self):
        """
        Returns the available charsets

        :rtype: list
        """
        d = super(WCDMAWrapper, self).get_charsets()
        d.addCallback(lambda resp: [match.group('lang') for match in resp])
        return d

    def get_contact(self, index):
        """Returns the contact at ``index``"""
        d = super(WCDMAWrapper, self).get_contact(index)
        d.addCallback(lambda match: regexp_to_contact(match[0]))
        return d

    def get_hardware_info(self):
        """Returns the manufacturer name, card model and firmware version"""
        dlist = [self.get_manufacturer_name(),
                self.get_card_model(),
                self.get_card_version()]

        return defer.gatherResults(dlist)

    def get_imei(self):
        """Returns the IMEI"""
        d = super(WCDMAWrapper, self).get_imei()
        d.addCallback(lambda response: response[0].group('imei'))
        return d

    def get_imsi(self):
        """Returns the IMSI"""
        d = super(WCDMAWrapper, self).get_imsi()
        d.addCallback(lambda response: response[0].group('imsi'))
        return d

    def get_ip4_config(self):
        """Returns the IP4Config info related to IpMethod"""
        raise NotImplementedError()

    def get_manufacturer_name(self):
        """Returns the manufacturer name"""
        d = super(WCDMAWrapper, self).get_manufacturer_name()
        d.addCallback(lambda response: response[0].group('name'))
        return d

    def get_netreg_info(self):
        """Get the registration status and the current operator"""
        # Ugly but it works. The naive approach with DeferredList won't work
        # as the call order is not guaranteed
        resp = []
        d = self.get_netreg_status()
        d.addCallback(lambda info: resp.append(info[1]))
        d.addCallback(lambda _: self.set_network_info_format(3, 2))
        d.addCallback(lambda _: self.get_network_info())
        d.addCallback(lambda info: resp.append(info[0]))

        def get_netinfo_eb(failure):
            failure.trap(E.NoNetwork)
            resp.append("0")

        d.addErrback(get_netinfo_eb)
        d.addCallback(lambda _: self.set_network_info_format(3, 0))
        d.addCallback(lambda _: self.get_network_info())
        d.addCallback(lambda info: resp.append(info[0]))
        d.addErrback(get_netinfo_eb)
        d.addCallback(lambda _: tuple(resp))
        return d

    def get_netreg_status(self):
        """Returns a tuple with the network registration status"""
        d = super(WCDMAWrapper, self).get_netreg_status()

        def get_netreg_status(resp):
            # convert them to int
            return int(resp[0].group('mode')), int(resp[0].group('status'))

        d.addCallback(get_netreg_status)
        return d

    def get_network_info(self):
        """
        Returns the network info  (a.k.a AT+COPS?)

        The response will be a tuple as (OperatorName, ConnectionType) if
        it returns a (None, None) that means that some error occurred while
        obtaining the info. The class that requested the info should take
        care of insisting before this problem. This method will convert
        numeric network IDs to alphanumeric.
        """
        d = super(WCDMAWrapper, self).get_network_info()

        def get_net_info_cb(netinfo):
            """
            Returns a (Networname, ConnType) tuple

            It returns None if there's no info
            """
            if not netinfo:
                return None

            netinfo = netinfo[0]

            if netinfo.group('error'):
                # this means that we've received a response like
                # +COPS: 0 which means that we don't have network temporaly
                # we should raise an exception here
                raise E.NoNetwork()

            status = int(netinfo.group('status'))
            conn_type = (status == 0) and 'GPRS' or '3G'
            netname = netinfo.group('netname')

            if netname in ['Limited Service',
                    pack_ucs2_bytes('Limited Service')]:
                raise ex.LimitedServiceNetworkError

            # netname can be in UCS2, as a string, or as a network id (int)
            if check_if_ucs2(netname):
                return unpack_ucs2_bytes(netname), conn_type
            else:
                # now can be either a string or a network id (int)
                try:
                    netname = int(netname)
                except ValueError:
                    # we got a string ID
                    return netname, conn_type

                # if we have arrived here, that means that the network id
                # is a five digit integer
                return str(netname), conn_type

        d.addCallback(get_net_info_cb)
        return d

    def get_network_mode(self):
        """Returns the current network mode"""
        raise NotImplementedError()

    def get_network_modes(self):
        """Returns the supported network modes"""
        return defer.succeed(sorted(self.custom.conn_dict.keys()))

    def get_network_names(self):
        """
        Performs a network search

        :rtype: list of :class:`NetworkOperator`
        """
        d = super(WCDMAWrapper, self).get_network_names()
        d.addCallback(lambda resp:
                [NetworkOperator(*match.groups()) for match in resp])
        return d

    def _get_free_contact_ids(self):
        """Returns a deque with the not used contact ids"""

        def list_contacts_cb(contacts):
            if not contacts:
                return deque(range(1, self.device.sim.size))

            busy_ids = [contact.index for contact in contacts]
            free = set(range(1, self.device.sim.size)) ^ set(busy_ids)
            return deque(list(free))

        def list_contacts_eb(failure):
            failure.trap(E.NotFound, E.GenericError)
            return deque(range(1, self.device.sim.size))

        d = self.list_contacts()
        d.addCallbacks(list_contacts_cb, list_contacts_eb)
        return d

    def _get_next_contact_id(self):
        """
        Returns the next unused contact id

        Provides some error control and won't fail if sim.size
        is None as the card might be a bit difficult
        """

        def do_get_it():
            d = self._get_free_contact_ids()
            d.addCallback(lambda free: free.popleft())
            return d

        if self.device.sim.size and self.device.sim.size != 0:
            return do_get_it()

        deferred = defer.Deferred()
        self.state_dict['phonebook_retries'] = 0

        def get_it(auxdef=None):

            def get_phonebook_size_cb(size):
                self.device.sim.size = size
                d = do_get_it()
                d.chainDeferred(deferred)

            def get_phonebook_size_eb(failure):
                self.state_dict['phonebook_retries'] += 1
                if self.state_dict['phonebook_retries'] > RETRY_ATTEMPTS:
                    raise RuntimeError("Could not obtain phonebook size")

                reactor.callLater(RETRY_TIMEOUT, get_it, auxdef)

            d = self.get_phonebook_size()
            d.addCallback(get_phonebook_size_cb)
            d.addErrback(get_phonebook_size_eb)

            return auxdef

        return get_it(deferred)

    def get_phonebook_size(self):
        """Returns the phonebook size"""
        d = super(WCDMAWrapper, self).get_phonebook_size()
        d.addCallback(lambda resp: int(resp[0].group('size')))
        return d

    def get_pin_status(self):
        """Returns 1 if PIN auth is active and 0 if its not"""

        def pinreq_errback(failure):
            failure.trap(E.SimPinRequired)
            return 1

        def aterror_eb(failure):
            failure.trap(E.GenericError)
            # return the failure or wont work
            return failure

        d = super(WCDMAWrapper, self).get_pin_status()
        d.addCallback(lambda response: int(response[0].group('status')))
        d.addErrback(pinreq_errback)
        d.addErrback(aterror_eb)

        return d

    def get_radio_status(self):
        """Returns whether the radio is enabled or disabled"""
        d = super(WCDMAWrapper, self).get_radio_status()
        d.addCallback(lambda resp: int(resp[0].group('status')))
        return d

    def get_roaming_ids(self):
        """Returns the network ids stored in the SIM to roam"""
        # a.k.a. AT+CPOL?
        d = super(WCDMAWrapper, self).get_roaming_ids()
        d.addCallback(lambda raw:
                [BasicNetworkOperator(obj.group('netid')) for obj in raw])
        return d

    def get_signal_quality(self):
        """Returns the signal level quality"""
        d = super(WCDMAWrapper, self).get_signal_quality()
        d.addCallback(lambda response: int(response[0].group('rssi')))
        return d

    def get_sms(self, index):
        return self.mal.get_sms(index)

    def do_get_sms(self, index):
        """
        Returns a ``Message`` object representing the SMS at ``index``
        """
        d = super(WCDMAWrapper, self).get_sms(index)

        def get_sms_cb(rawsms):
            try:
                sms = Message.from_pdu(rawsms[0].group('pdu'))
                sms.where = int(rawsms[0].group('where'))
                sms.index = index
            except IndexError:
                # handle bogus CMTI notifications, see #180
                return None

            return sms

        d.addCallback(get_sms_cb)
        return d

    def get_sms_format(self):
        """
        Returns 1 if SMS format is text and 0 if SMS format is PDU
        """
        d = super(WCDMAWrapper, self).get_sms_format()
        d.addCallback(lambda response: int(response[0].group('format')))
        return d

    def get_smsc(self):
        """Returns the SMSC number stored in the SIM"""
        d = super(WCDMAWrapper, self).get_smsc()

        def get_smsc_cb(response):
            try:
                smsc = response[0].group('smsc')
                if not smsc.startswith('+'):
                    if check_if_ucs2(smsc):
                        smsc = from_u(unpack_ucs2_bytes(smsc))

                return smsc
            except KeyError:
                raise E.NotFound()

        d.addCallback(get_smsc_cb)
        return d

    def list_contacts(self):
        """
        Returns all the contacts in the SIM

        :rtype: list
        """

        def not_found_eb(failure):
            failure.trap(E.NotFound, E.InvalidIndex, E.GenericError)
            return []

        def get_them(ignored=None):
            d = super(WCDMAWrapper, self).list_contacts()
            d.addCallback(lambda matches: map(regexp_to_contact, matches))
            d.addErrback(not_found_eb)
            return d

        if self.device.sim.size:
            return get_them()
        else:
            d = self._get_next_contact_id()
            d.addCallback(get_them)
            return d

    def list_sms(self):
        return self.mal.list_sms()

    def do_list_sms(self):
        """
        Returns all the SMS in the SIM card

        :rtype: list
        """
        d = super(WCDMAWrapper, self).list_sms()

        def get_all_sms_cb(messages):
            sms_list = []
            for rawsms in messages:
                try:
                    sms = Message.from_pdu(rawsms.group('pdu'))
                    sms.index = int(rawsms.group('id'))
                    sms.where = int(rawsms.group('where'))
                    sms_list.append(sms)
                except ValueError:
                    log.err(ex.MalformedSMSError,
                            "Malformed PDU: %s" % rawsms.group('pdu'))
            return sms_list

        d.addCallback(get_all_sms_cb)
        return d

    def save_sms(self, sms):
        return self.mal.save_sms(sms)

    def do_save_sms(self, sms):
        """
        Stores ``sms`` and returns a list of indexes

        ``sms`` might span several messages if it is a multipart SMS
        """
        save_sms = super(WCDMAWrapper, self).save_sms
        ret = [save_sms(pdu, p_len) for p_len, pdu in sms.to_pdu(store=True)]
        d = defer.gatherResults(ret)
        # the order is important! You need to run gatherResults and add
        # the callback to its result, not the other way around!
        d.addCallback(lambda response:
                         [int(resp[0].group('index')) for resp in response])
        return d

    def send_at(self, atstr, name='send_at', callback=None):
        """Sends an arbitrary AT string ``atstr``"""
        d = super(WCDMAWrapper, self).send_at(atstr, name=name)
        if callback is None:
            d.addCallback(lambda response: response[0].group('resp'))
        else:
            d.addCallback(callback)

        return d

    def send_pin(self, pin):
        """
        Sends ``pin`` to authenticate

        Most devices need some time to settle after a successful auth
        it is the caller's responsability to give at least 15 seconds
        to the device to settle, this time varies from device to device
        """
        d = super(WCDMAWrapper, self).send_pin(pin)
        d.addCallback(lambda response: response[0].group('resp'))
        return d

    def send_puk(self, puk, pin):
        """
        Send ``puk`` and ``pin`` to authenticate

        Most devices need some time to settle after a successful auth
        it is the caller's responsability to give at least 15 seconds
        to the device to settle, this time varies from device to device
        """
        d = super(WCDMAWrapper, self).send_puk(puk, pin)
        d.addCallback(lambda response: response[0].group('resp'))
        return d

    def send_sms(self, sms):
        """
        Sends ``sms`` and returns the indexes

        ``sms`` might span several messages if it is a multipart SMS
        """

        def send_sms_cb(response):
            return int(response[0].group('index'))

        ret = []
        for pdu_len, pdu in sms.to_pdu():
            d = super(WCDMAWrapper, self).send_sms(pdu, pdu_len)
            d.addCallback(send_sms_cb)
            ret.append(d)

        return defer.gatherResults(ret)

    def send_sms_from_storage(self, index):
        return self.mal.send_sms_from_storage(index)

    def do_send_sms_from_storage(self, index):
        """Sends the SMS stored at ``index`` and returns the new index"""
        d = super(WCDMAWrapper, self).send_sms_from_storage(index)
        d.addCallback(lambda response: int(response[0].group('index')))
        return d

    def set_apn(self, apn):
        """Sets the APN to ``apn``"""

        def process_apns(apns):
            state = self.state_dict
            for _index, _apn in apns:
                if apn == _apn:
                    state['conn_id'] = _index
                    return

            state['conn_id'] = len(apns) + 1
            d = super(WCDMAWrapper, self).set_apn(state['conn_id'], apn)
            d.addCallback(lambda response: response[0].group('resp'))
            return d

        d = self.get_apns()
        d.addCallback(process_apns)
        return d

    def set_band(self, band):
        """Sets the device band to ``band``"""
        raise NotImplementedError()

    def set_charset(self, charset):
        """Sets the SIMs charset to ``charset``"""
        d = super(WCDMAWrapper, self).set_charset(charset)
        d.addCallback(lambda ignored: self.device.sim.set_charset(charset))
        return d

    def set_network_mode(self, mode):
        """Sets the network mode to ``mode``"""
        raise NotImplementedError()

    def enable_radio(self, enable):
        """
        Enables the radio according to ``enable``

        It will not enable it if its already enabled and viceversa
        """
        if self.device.status >= DEV_ENABLED and enable:
            # no need to enable an enabled device
            return defer.succeed("OK")

        def check_if_necessary(status):
            if (status and enable) or (not status and not enable):
                return defer.succeed('OK')

            d = super(WCDMAWrapper, self).enable_radio(enable)
            d.addCallback(lambda response: response[0].group('resp'))
            return d

        d = self.get_radio_status()
        d.addCallback(check_if_necessary)
        return d

    def set_sms_format(self, _format=0):
        """Sets PDU mode or text mode in the SIM"""
        d = super(WCDMAWrapper, self).set_sms_format(_format)
        d.addCallback(lambda response: response[0].group('resp'))
        return d

    def set_smsc(self, smsc):
        """Sets the SIMS's SMSC number to ``smsc``"""
        if 'UCS2' in self.device.sim.charset:
            smsc = pack_ucs2_bytes(smsc)

        d = super(WCDMAWrapper, self).set_smsc(smsc)
        d.addCallback(lambda response: response[0].group('resp'))
        return d

    # some high-level methods exported over DBus
    def init_properties(self):

        def set_property(name, what, iface=CRD_INTFACE):
            self.device.props[iface][name] = what

        d = self.get_bands()
        d.addCallback(lambda bands: set_property('SupportedBands', bands))
        d.addCallback(lambda _: self.get_network_modes())
        d.addCallback(lambda modes: set_property('SupportedModes', modes))
        d.addCallback(lambda _: self.get_pin_status())
        d.addCallback(lambda active: set_property('PinEnabled', bool(active)))
        return d

    def get_simple_status(self):
        """Returns the status for o.fd.MM.Modem.Simple.GetStatus"""

        def get_simple_status_cb((rssi, netinfo, band, net_mode)):
            return dict(signal_quality=rssi,
                        operator_code=netinfo[1],
                        operator_name=netinfo[2],
                        band=band)

        deferred_list = []
        deferred_list.append(self.get_signal_quality())
        deferred_list.append(self.get_netreg_info())
        deferred_list.append(self.get_band())
        deferred_list.append(self.get_network_mode())

        d = defer.gatherResults(deferred_list)
        d.addCallback(get_simple_status_cb)
        d.addErrback(log.err)
        return d

    def connect_simple(self, settings):
        """Connects with the given ``settings``"""
        simplesm = self.device.custom.simp_klass(self.device, settings)
        d = simplesm.start_simple()
        d.addCallback(lambda _: self.device.set_status(DEV_CONNECTED))
        return d

    def connect_to_internet(self, number):
        """Opens data port and dials ``number`` in"""
        # open the data port
        port = self.device.ports.dport
        # this will raise a SerialException if port is busy
        port.obj = serial.Serial(port.path)
        port.obj.flush()
        # send ATDT and convert number to string as pyserial does
        # not like to write unicode to serial ports
        d = defer.maybeDeferred(port.obj.write,
                                "ATDT%s\r\n" % str(number))
        d.addCallback(lambda _: self.device.set_status(DEV_CONNECTED))
        return d

    def disconnect_from_internet(self):
        """Disconnects the modem temporally lowering the DTR"""
        port = self.device.ports.dport
        if not port.obj.isOpen():
            raise AttributeError("Data serial port is not open")

        def restore_speed(d, speed):
            port.obj.setBaudrate(speed)
            port.obj.close()
            self.device.set_status(DEV_ENABLED)
            d.callback(True)

        d = defer.Deferred()
        # lower and raise baud speed
        speed = port.obj.getBaudrate()
        port.obj.setBaudrate(0)
        reactor.callLater(.1, restore_speed, d, speed)
        return d

    def register_with_netid(self, netid):
        """
        I will try my best to register with ``netid``

        If ``netid`` is an empty string, I will register with my home network
        """
        netr_klass = self.device.custom.netr_klass
        netsm = netr_klass(self.device.sconn, netid)
        return netsm.start_netreg()

    def enable_device(self, enable):
        """
        I enable or disable myself according to ``enable``

        If enable is True, I check the auth state of a device and will try to
        initialize it. Otherwise I will disable myself
        """
        if enable:
            return self._do_enable_device()
        else:
            return self._do_disable_device()

    def _do_disable_device(self):
        if self.device.status == DEV_CONNECTED:

            def on_disconnect_from_internet(_):
                self.device.set_status(DEV_ENABLED)
                self.device.close()

            d = self.disconnect_from_internet()
            d.addCallback(on_disconnect_from_internet)
            d.addErrback(log.err)
            return d

        if self.device.status == DEV_ENABLED:
            return self.device.close()

    def _do_enable_device(self):
        from wader.common.startup import attach_to_serial_port
        if self.device.status == DEV_ENABLED:
            return defer.succeed(self.device)

        if self.device.status == DEV_AUTHENTICATED:
            # if a device was enabled and then disabled, there's no
            # need to check the authentication again
            d = attach_to_serial_port(self.device)
            d.addCallback(self.device.initialize)
            return d

        def process_device_and_initialize(device):
            self.device = device
            auth_klass = self.device.custom.auth_klass
            authsm = auth_klass(self.device)
            d = authsm.start_auth()
            # if auth is ready, the device will initialize straight away
            # if auth aint ready the callback chain wont be executed and
            # will just return the given exception
            d.addCallback(self.device.initialize)
            return d

        d = attach_to_serial_port(self.device)
        d.addCallback(process_device_and_initialize)
        return d

    def _check_initted_device(self, result):
        """
        Upon successful auth over DBus I'll check if the device was initted
        """
        if self.device.status == DEV_AUTHENTICATED:
            log.msg("device was already initted, just returning orig result")
            return result

        DELAY = self.device.custom.auth_klass.DELAY
        log.msg("giving the device %d seconds to settle, waiting..." % DELAY)

        deferred = defer.Deferred()

        def do_init():
            d = self.device.initialize()
            d.addCallback(deferred.callback)

        reactor.callLater(DELAY, do_init)
        return deferred


class BasicNetworkOperator(object):
    """A Network operator with a netid"""

    def __init__(self, netid):
        super(BasicNetworkOperator, self).__init__()
        if check_if_ucs2(netid):
            self.netid = from_ucs2(netid)
        else:
            self.netid = netid

    def __repr__(self):
        return '<BasicNetworkOperator: %s>' % self.netid

    def __eq__(self, o):
        return self.netid == o.netid

    def __ne__(self, o):
        return not self.__eq__(o)


class NetworkOperator(BasicNetworkOperator):
    """I represent a network operator on a mobile network"""

    def __init__(self, stat, long_name, short_name, netid, rat):
        super(NetworkOperator, self).__init__(netid)
        self.stat = int(stat)
        self.long_name = from_ucs2(long_name)
        self.short_name = from_ucs2(short_name)
        self.rat = int(rat)

    def __repr__(self):
        args = (self.long_name, self.netid)
        return '<NetworkOperator "%s" netid: %s>' % args
