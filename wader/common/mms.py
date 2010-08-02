# -*- coding: utf-8 -*-
# Copyright (C) 2008-2010  Warp Networks, S.L.
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
"""MMS related classes and functions"""

from array import array
from cStringIO import StringIO
from urlparse import urlparse

from twisted.internet import reactor
from twisted.internet.defer import Deferred, succeed
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from twisted.web.iweb import IBodyProducer
from zope.interface import implements

from messaging.mms.message import MMSMessage, DataPart
import wader.common.aterrors as E


class BinaryDataProducer(object):
    """Binary data producer for HTTP POSTs"""
    implements(IBodyProducer)

    def __init__(self, data):
        self.data = data
        self.length = len(data)

    def startProducing(self, consumer):
        consumer.write(self.data)
        return succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass


class BinaryDataConsumer(Protocol):
    """Binary data consumer for HTTP GETs"""

    def __init__(self, finished):
        self.finished = finished
        self.received = StringIO()

    def dataReceived(self, data):
        self.received.write(data)

    def connectionLost(self, reason):
        print 'Finished receiving body:', reason.getErrorMessage()
        self.finished.callback(self.received.getvalue())
        self.received.close()


def mms_to_dbus_data(mms):
    """Converts ``mms`` to a dict ready to be sent via DBus"""
    dbus_data = {}
    # Convert headers
    for key, val in mms.headers.items():
        if key == 'Content-Type':
            dbus_data[key] = val[0]
        else:
            dbus_data[key] = val

    # Set up data
    dbus_data['data-parts'] = []
    for data_part in mms.data_parts:
        part = {'Content-Type': data_part.content_type, 'data': data_part.data}
        if data_part.headers['Content-Type'][1]:
            part['parameters'] = data_part.headers['Content-Type'][1]

        dbus_data['data-parts'].append(part)

    return dbus_data


def dbus_data_to_mms(dbus_data):
    """Returns a `MMSMessage` out of ``dbus_data``"""
    mms = MMSMessage()

    # add data parts
    for data_part in dbus_data['data-parts']:
        content_type = data_part['Content-Type']
        data = array("B", data_part['data'])
        parameters = data_part.get('parameters', {})

        dp = DataPart()
        dp.set_data(data, content_type, parameters)
        # XXX: MMS message with no SMIL support

        # Content-Type: application/vnd.wap.multipart.mixed
        mms.add_data_part(dp)

    return mms


def response_callback(response):
    """
    generic callback for GET requests where we are interested in the result

    It will raise an `ExpiredNotification` if the content is not available
    """
    if response.code != 200:
        if response.code == 404:
            raise E.ExpiredNotification("Notification expired")

        args = (response.code, response.phrase)
        raise E.ExpiredNotification("Unknown error (%d): %s" % args)

    finished = Deferred()
    response.deliverBody(BinaryDataConsumer(finished))
    return finished


def post_callback(response):
    """
    generic callback for POST request where we are interested in the result

    """
    if response.code != 200:
        # XXX: Choose a good error name...
        pass

    finished = Deferred()
    response.deliverBody(BinaryDataConsumer(finished))
    return finished


def get_payload(uri, extra_info):
    # if gateway == 202.202.202.202:7899
    # and url = http://promms/fooBAR
    # then telnet 202.202.202.202 7899
    # GET /fooBAR
    # Host: promms
    o = urlparse(uri)

    header_data = {
        'Host': [o.netloc],
    }
    headers = Headers(header_data)

    get_url = "%s:%s%s" % (extra_info['gateway'], extra_info['port'], o.path)

    agent = Agent(reactor)
    d = agent.request('GET', get_url, headers, None)
    d.addCallback(response_callback)
    d.addCallback(MMSMessage.from_data)
    return d


def post_payload(uri, data, headers=None):
    if headers is not None:
        headers = Headers(headers)

    agent = Agent(reactor)
    body = BinaryDataProducer(data)
    return agent.request('POST', uri, headers, body)


def send_m_notifyresp_ind(uri, tx_id, headers=None):
    message = MMSMessage()
    message.headers['Transaction-Id'] = tx_id
    message.headers['Message-Type'] = 'm-notifyresp-ind'
    message.headers['Status'] = 'Retrieved'

    return post_payload(uri, message.encode(), headers)


def send_m_send_req(uri, dbus_data):
    # sanitize headers
    headers = dbus_data['headers']
    if 'To' not in headers:
        raise ValueError("You need to provide a recipient 'To'")

    if not headers['To'].endswith('/TYPE=PLMN'):
        headers['To'] += '/TYPE=PLMN'

    # set headers
    mms = dbus_data_to_mms(dbus_data)
    for key, val in headers.items():
        mms.headers[key] = val

    # set type the last one so is always the right type
    mms.headers['Message-Type'] = 'm-send-req'

    d = post_payload(uri, mms.encode(), headers)
    d.addCallback(post_callback)
    d.addCallback(MMSMessage.from_data)
    return d
