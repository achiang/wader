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
"""SMS storage layer"""

from datetime import datetime
import sqlite3
from time import mktime

from wader.common.contact import Contact as _Contact
from wader.common.encoding import to_u
from wader.common.sms import Message as _Message

INBOX, OUTBOX, DRAFTS = 1, 2, 3
UNREAD, READ = 0x01, 0x02
# GSM spec
# 0 - Unread message that has been received
# 1 - Read message that has been received
# 2 - Unsent message that has been stored
# 3 - Sent message that has been stored
# 4 - Any message

CONTACTS_SCHEMA = """
create table contact (
    id integer primary key autoincrement,
    name text not null,
    number text not null,
    email text,
    picture blob);

create table version (
    version integer default 1);
"""

SMS_SCHEMA = """
create table message (
    id integer primary key autoincrement,
    date integer not null,
    number text not null,
    text text,
    flags integer,
    thread_id integer not null constraint fk_thread_id references thread(id) on delete cascade);

create table thread (
    id integer primary key autoincrement,
    date integer default 0,                 -- updated by trigger
    number text not null,                   -- specified in creation
    message_count integer default 0,        -- updated by trigger
    snippet text,                           -- updated by trigger
    read integer default 0,                 -- updated by trigger
    folder_id integer not null constraint fk_folder_id references folder(id) on delete cascade);

create table folder (
    id integer primary key autoincrement,
    name text not null);

create table version (
    version integer default 1);

create index message_flags_index on message(flags);
create index message_thread_index on message(thread_id, id);
create index thread_folder_index on thread(folder_id, id);

-- delete on cascade thread -> message
create trigger fkd_thread_message before delete on "thread"
    when exists (select 1 from "message" where old."id" == "thread_id")
begin
    delete from "message" where "thread_id" = old."id";
end;

-- delete on cascade folder -> thread
create trigger fkd_folder_thread before delete on "folder"
    when exists (select 1 from "thread" where old."id" == "folder_id")
begin
    delete from "thread" where "folder_id" = old."id";
end;

-- prevent insertion of messages with an invalid thread_id
create trigger fki_message_thread before insert on "message"
    when new."thread_id" is not null and not exists (select 1 from "thread" where new."thread_id" == "id")
begin
    select raise(abort, 'constraint fki_message_thread failed: thread_id does not exist in thread table');
end;

-- update snippet, message_count and date of thread upon message insertion
create trigger fki_update_thread_values after insert on "message"
    when new."thread_id" is not null and exists (select 1 from "thread" where new."thread_id" == "id")
begin
    update "thread"
    set
        snippet = substr(new."text", 0, 100),
        message_count = (select message_count from thread where id = new."thread_id") + 1,
        date = strftime('%s', 'now')
    where id = new."thread_id";
    update "thread"
    set
        read = (select read from thread where id = new."thread_id") + 1
    where id = new."thread_id" and msg_is_read(new."flags");
end;

create trigger fku_mark_message_read after update on "message"
    when not msg_is_read(old."flags") and msg_is_read(new."flags")
begin
    update "thread"
    set
        read = (select read from thread where id = new."thread_id") + 1
    where id = new."thread_id";
end;

create trigger fku_mark_message_unread after update on "message"
    when msg_is_read(old."flags") and not msg_is_read(new."flags")
begin
    update "thread"
    set
        read = (select read from thread where id = new."thread_id") - 1
    where id = new."thread_id";
end;

-- prevent thread.id updates when there are messages associated to it
create trigger fku_thread_message after update of id on "thread"
    when exists (select 1 from "message" where old."id" == "thread_id")
begin
    select raise(abort, 'constraint fku_thread_message failed: can not update thread.id as there are messages associated to it');
end;

-- prevent message.thread_id updates with non existing thread.id
create trigger fku_message_thread before update of thread_id on "message"
    when new."thread_id" is not null and not exists (select 1 from "thread" where new."thread_id" == "id")
begin
    select raise(abort, 'constraint fku_message_thread failed: can not update message.thread_id with non existing thread_id');
end;

create trigger fki_thread_folder before insert on "thread"
    when new."folder_id" is not null and not exists (select 1 from "folder" where new."folder_id" == "id")
begin
    select raise(abort, 'constraint fki_thread_folder failed: folder_id does not exist in folder table');
end;

create trigger fku_folder_thread after update of id on "folder"
    when exists (select 1 from "thread" where old."id" == "folder_id")
begin
    select raise(abort, 'constraint fku_folder_thread failed: can not update folder.id as there are threads associated to it');
end;

create trigger fku_thread_folder before update of folder_id on "thread"
    when new."folder_id" is not null and not exists (select 1 from "folder" where new."folder_id" == "id")
begin
    select raise(abort, 'constraint fku_thread_folder failed: can not update thread.folder_id as it does not exist');
end;

-- decrease thread.message_count after deleting a message
create trigger fkd_update_message_count after delete on "message"
    when old."thread_id" is not null
begin
    update "thread"
    set message_count = (select message_count from thread where id = old.thread_id) - 1
    where id = old."thread_id";
end;
"""

def message_read(flags):
    """
    Returns a bool indicating whether the message had been read or not
    """
    # second bit is the "was read" flag
    return (int(flags) & READ) >> 1

def get_value_and_pop(kw, name, d=None):
    """kw.pop[name] if name in kw, else d. d defaults to None"""
    return (kw.pop(name) if name in kw else d)

class Contact(_Contact):
    """I am a :class:`_Contact` with email and a picture"""
    def __init__(self, *args, **kw):
        self.email = to_u(get_value_and_pop(kw, 'email', ''))
        self.picture = get_value_and_pop(kw, 'picture', '')
        super(Contact, self).__init__(*args, **kw)

    @classmethod
    def from_row(cls, row):
        """Returns a :class:`Contact` out of ``row``"""
        return cls(row[1], row[2], index=row[0], email=row[3], picture=row[4])

    def to_row(self):
        """Returns a tuple object ready to be inserted in the DB"""
        return (self.index, self.name, self.number, self.email, self.picture)


class Folder(object):
    """I am a container for threads and messages"""
    def __init__(self, name, index=None):
        self.name = name
        self.index = index

    def __repr__(self):
        return "<Folder index: %d name: %s>" % (self.index, self.name)

    def __eq__(self, other):
        return self.index == other.index

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def from_row(cls, row):
        """Returns a :class:`Folder` out of ``row``"""
        return cls(row[1], row[0])

    def to_row(self):
        """Returns a tuple object ready to be inserted in the DB"""
        return (self.index, self.name)


inbox_folder = Folder("Inbox", 1)
outbox_folder = Folder("Outbox", 2)
drafts_folder = Folder("Drafts", 3)


class Message(_Message):
    """I am a :class:`_Message` that belongs to a thread and has flags"""
    def __init__(self, *args, **kw):
        self.flags = get_value_and_pop(kw, 'flags', READ)
        self.thread = get_value_and_pop(kw, 'thread')
        super(Message, self).__init__(*args, **kw)

    def __repr__(self):
        args = (self.index, self.thread.index)
        return "<Message index %d thread_id %d>" % args

    def to_row(self):
        """Returns a tuple ready to be added to the provider DB"""
        return (self.index, mktime(self.datetime.timetuple()), self.number,
                self.text, self.flags, self.thread.index)

    @classmethod
    def from_row(cls, row, thread=None):
        return cls(row[2], row[3], index=row[0], flags=row[4],
                   _datetime=datetime.fromtimestamp(row[1]), thread=thread)


class Thread(object):
    """I represent an SMS thread in the DB"""
    def __init__(self, _datetime, number, index=None, message_count=1,
                 snippet='', read=1, folder=None):
        super(Thread, self).__init__()
        self.datetime = _datetime
        self.number = number
        self.index = index
        self.message_count = message_count
        self.snippet = snippet
        self.read = read
        self.folder = folder

    def __repr__(self):
        return "<Thread %d>" % self.index

    def __eq__(self, other):
        return self.index == other.index

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def from_row(cls, row, folder=None):
        """Returns a :class:`Thread` out of ``row``"""
        return cls(datetime.fromtimestamp(row[1]), row[2], index=row[0],
                   message_count=row[3], snippet=row[4], read=row[5],
                   folder=folder)

    def to_row(self):
        """Returns a tuple ready to be inserted in the DB"""
        return (self.index, mktime(self.datetime.timetuple()), self.number,
                self.message_count, self.snippet, self.read, self.folder.index)


class DBError(Exception):
    """Base class for DB related errors"""


class DBProvider(object):
    """Base class for the DB providers"""
    def __init__(self, path, schema):
        self.conn = sqlite3.connect(path, isolation_level=None)
        c = self.conn.cursor()
        try:
            c.executescript(schema)
        except sqlite3.OperationalError:
            # ignore error, the database already exists
            pass

    def close(self):
        """Closes the provider and frees resources"""
        self.conn.close()


class ContactProvider(DBProvider):
    """DB contacts provider"""
    def __init__(self, path):
        super(ContactProvider, self).__init__(path, CONTACTS_SCHEMA)

    def add_contact(self, contact):
        """
        Adds ``contact`` to the DB returning the object updated with index
        """
        c = self.conn.cursor()
        c.execute("insert into contact values (?, ?, ?, ?, ?)",
                  contact.to_row())
        contact.index = c.lastrowid
        return contact

    def delete_contact(self, contact):
        """Deletes ``contact`` from the DB"""
        c = self.conn.cursor()
        c.execute("delete from contact where id=?", (contact.index,))

    def edit_contact(self, contact):
        """
        Edits ``contact`` with the new attributes

        The index can not change, so we'll update the rest
        """
        c = self.conn.cursor()
        args = (contact.name, contact.number, contact.email, contact.picture,
                contact.index)
        c.execute("""update contact set name = ?, number = ?,
                     email = ?, picture = ? where id = ?""", args)
        return contact

    def list_contacts(self):
        """Returns an iterator with all the contacts in DB"""
        c = self.conn.cursor()
        c.execute("select * from contact")
        return (Contact.from_row(row) for row in c.fetchall())


class SmsProvider(DBProvider):
    """DB Sms provider"""
    def __init__(self, path):
        super(SmsProvider, self).__init__(path, SMS_SCHEMA)
        self.conn.create_function('msg_is_read', 1, message_read)

    def add_folder(self, folder):
        """
        Adds ``folder`` to the DB and returns the object updated with index
        """
        c = self.conn.cursor()
        c.execute("insert into folder values (?, ?)", folder.to_row())
        folder.index = c.lastrowid
        return folder

    def add_thread(self, thread):
        """
        Adds ``thread`` to the DB and returns the object updated with index
        """
        c = self.conn.cursor()
        c.execute("insert into thread values (?, ?, ?, ?, ?, ?, ?)",
                  thread.to_row())
        thread.index = c.lastrowid
        return thread

    def add_sms(self, sms):
        """
        Adds ``sms`` to the DB and returns the object updated with index
        """
        c = self.conn.cursor()
        if sms.thread is None:
            # create a new thread for this sms
            thread = self.get_thread_by_number(sms.number)
            sms.thread = thread

        c.execute("insert into message values (?, ?, ?, ?, ?, ?)",
                  sms.to_row())
        sms.index = c.lastrowid
        return sms

    def delete_folder(self, folder):
        """Deletes ``folder`` from the DB"""
        # Folders 1, 2, 3 can not be deleted (Inbox, Outbox, Drafts)
        if folder.index <= 3:
            raise DBError("Folder %d can not be deleted" % folder.index)

        c = self.conn.cursor()
        c.execute("delete from folder where id=?", (folder.index,))

    def delete_sms(self, sms):
        """Deletes ``sms`` from the DB"""
        c = self.conn.cursor()
        c.execute("delete from message where id=?", (sms.index,))

    def delete_thread(self, thread):
        """Deletes ``thread`` from the DB"""
        c = self.conn.cursor()
        c.execute("delete from thread where id=?", (thread.index,))

    def _get_folder_by_id(self, index):
        """Returns the :class:`Folder` identified by ``index``"""
        c = self.conn.cursor()
        c.execute("select * from folder where id=?", (index,))
        try:
            return Folder.from_row(c.fetchone())
        except TypeError:
            raise DBError("Folder %d does not exist" % index)

    def _get_thread_by_id(self, index):
        """Returns the :class:`Thread` identified by ``index``"""
        c = self.conn.cursor()
        c.execute("select * from thread where id=?", (index,))
        try:
            row = c.fetchone()
            folder = self._get_folder_by_id(row[6])
            return Thread.from_row(row, folder=folder)
        except TypeError:
            raise DBError("Thread %d does not exist" % index)

    def get_thread_by_number(self, number, folder=inbox_folder):
        """
        Returns the :class:`Thread` that belongs to ``number`` under ``folder``

        :rtype: :class:`Thread`
        """
        c = self.conn.cursor()
        sql = "select * from thread where number like ? and folder_id=?"
        c.execute(sql, ("%%%s%%" % number, folder.index))
        if c.rowcount == 1:
            # there already exists a thread for this number under folder
            return Thread.from_row(c.fetchone())
        elif c.rowcount < 1:
            # create thread for this number
            thread = Thread(datetime.now(), number, folder=folder)
            return self.add_thread(thread)
        elif c.rowcount > 1:
            raise DBError("Too many threads associated to number %s" % number)

        raise DBError("No thread found for number %s" % number)

    def list_folders(self):
        """
        List all the :class:`Folder` objects in the DB

        :rtype: iter
        """
        c = self.conn.cursor()
        c.execute("select * from folder")
        return (Folder.from_row(row) for row in c.fetchall())

    def list_from_folder(self, folder):
        """
        List all the :class:`Thread` objects that belong to ``folder``

        :rtype: iter
        """
        c = self.conn.cursor()
        sql = "select * from thread where folder_id=? order by date desc"
        c.execute(sql, (folder.index,))
        return (Thread.from_row(row, folder=folder) for row in c.fetchall())

    def list_from_thread(self, thread):
        """
        List all the :class:`Message` objects that belong to ``thread``

        :rtype: iter
        """
        c = self.conn.cursor()
        sql = "select * from message where thread_id=? order by date desc"
        c.execute(sql, (thread.index,))
        return (Message.from_row(row, thread=thread) for row in c.fetchall())

    def list_threads(self):
        """
        List all the :class:`Thread` objects in the DB

        :rtype: iter
        """
        c = self.conn.cursor()
        c.execute("select * from thread order by date desc")
        for row in c:
            folder = self._get_folder_by_id(row[6])
            yield Thread.from_row(row, folder=folder)

    def list_sms(self):
        """
        List all the :class:`Message` objects in the DB

        :rtype: iter
        """
        c = self.conn.cursor()
        c.execute("select * from message order by date desc")
        for row in c:
            thread = self._get_thread_by_id(row[5])
            yield Message.from_row(row, thread=thread)

    def move_to_folder(self, src, dst):
        """
        Moves ``src`` to ``dst``

        :return: The updated ``src`` object
        """
        if not isinstance(dst, Folder):
            raise TypeError("dst must be a Folder instance")

        if isinstance(src, Thread):
            return self._move_thread_to_folder(src, dst)
        elif isinstance(src, Message):
            return self._move_sms_to_folder(src, dst)
        else:
            raise TypeError("src must be a Thread or a Folder instance")

    def update_sms_flags(self, sms, flags):
        """Updates ``sms`` with ``flags``"""
        c = self.conn.cursor()
        c.execute("update message set flags=? where id=?", (flags, sms.index))
        sms.flags = flags
        return sms

    def _move_sms_to_folder(self, sms, folder):
        c = self.conn.cursor()
        sql = "select id from thread where number like ? and folder_id=?"
        c.execute(sql, ("%%%s%%" % sms.number, folder.index))
        if c.rowcount == 1:
            # there already exists a thread for that number in folder
            thread = self._get_thread_by_id(c.fetchone()[0])
            c.execute("update message set thread_id=? where id=?",
                      (thread.index, sms.index))
            sms.thread = thread
            return sms
        elif c.rowcount < 1:
            # create thread for this number
            thread = self.add_thread(
                    Thread(sms.datetime, sms.number, folder=folder))
            c.execute("update message set thread_id=? where id=?",
                      (thread.index, sms.index))
            sms.thread = thread
            return sms
        else:
            msg = "Too many threads associated to number %s"
            raise DBError(msg % sms.number)

    def _move_thread_to_folder(self, thread, folder):
        c = self.conn.cursor()
        c.execute("update thread set folder_id=? where id=?",
                  (folder.index, thread.index))
        thread.folder = folder
        return thread

