#!/usr/bin/env python

# (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

import acom.data as acom_data
import time
import hashlib
import string
import random

def id_generator(size=160, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def cryptify(password, salt):
    m = hashlib.md5()
    m.update(password)
    m.update(salt)
    return m.hexdigest()

class Users(acom_data.Base):

    def __init__(self):

        self.REST = "/api/users/%s"
        self.TYPE = 'user'
        self.FIELDS = dict(
            primary  = 'name',
            required = [ '_password' ],
            optional = dict(),
            protected = [
                '_salt',
                '_created_date',
                '_modified_date',
            ],
            hidden = [ '_salt', '_password' ],
            private = []
        )
        super(Users, self).__init__()

    def compute_derived_fields_on_add(self, name, properties):
        info = self.lookup(name, internal=True)
        new_properties = {}
        new_properties['_created_date'] = time.time()

        # disabled until correct
        # TODO: crypt password and store salt also
        salt = new_properties['_salt'] = id_generator()
        passwd = info['_password']
        crypted = cryptify(passwd, salt)
        new_properties['_password'] = crypted

        self.edit(name, new_properties, internal=True, hook=True)

    def compute_derived_fields_on_edit(self, name, properties):
        new_properties = {}
        new_properties['_modified_date'] = time.time()

        data = self.lookup(name, internal=True)

        if '_password' in properties:
            passwd = properties['_password']
            crypted = cryptify(passwd, data['_salt'])
            new_properties['_password'] = crypted

        self.edit(name, new_properties, internal=True, hook=True)

    def login(self, name, password):
        try:
            record = self.lookup(name, internal=True)
        except acom_data.DoesNotExist:
            return False

        salt = record['_salt']
        crypted = cryptify(password, salt)
        return record['_password'] == crypted

if __name__ == '__main__':

    acom_data.test_mode()

    u = Users()
    u.clear_test_data()
    all = u.list()
    assert len(all) == 0     

    # error to add without a password!
    try:
        u.add(dict(name='timmy'))
        assert False
    except acom_data.InvalidInput:
        pass
 
    u.add(dict(name='timmy',_password='timmy1'))

    assert u.login('timmy','timmy1')
    assert not u.login('timmy','timmy2')

    timmy = u.lookup('timmy')
    assert '_password' not in timmy
    assert '_salt' not in timmy
    time1 = timmy['_created_date']

    all = u.list()
    assert len(all) == 1
    assert all[0]['name'] == 'timmy'
    assert '_password' not in all[0]

    u.edit('timmy', dict(_password='timmy2'))
   
    assert not u.login('timmy','timmy1')
    assert u.login('timmy','timmy2')

    timmy = u.lookup('timmy', internal=True)
    assert timmy['_password'] != 'timmy2'
    time2 = timmy['_created_date']
    time3 = timmy['_modified_date']
    assert time1 == time2
    assert time3 != time1

    u.delete('timmy')
    assert len(u.list()) == 0
    
    u.add(dict(name='timmy',_password='timmy1'))
    print "ok"

