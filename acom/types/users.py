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

class Users(acom_data.Base):

    def __init__(self):

        self.TYPE = 'user'
        self.FIELDS = dict(
            primary  = 'name',
            required = [ 'password' ],
            optional = dict(),
            protected = [
                'created_date',
                'modified_date',
                'salt'
            ],
            hidden = [ 'password' ],
            private = []
        )
        super(Users, self).__init__()

    def compute_derived_fields_on_add(self, name, properties):
        new_properties = {}
        new_properties['created_date'] = time.time()
        # TODO: crypt password and store salt also
        self.edit(name, new_properties, internal=True, hook=True)

    def compute_derived_fields_on_edit(self, name, properties):
        new_properties = {}
        new_properties['modified_date'] = time.time()
        self.edit(name, new_properties, internal=True, hook=True)

    def login(self, name, password):
        try:
            record = self.lookup(name, internal=True)
        except acom_data.DoesNotExist:
            return False
        return record['password'] == password

if __name__ == '__main__':

    acom_data.test_mode()

    u = Users()
    u.clear_test_data()
    all = u.list()
    assert len(all) == 0     

    # error to add without a password!
    try:
        u.add('timmy', dict())
        assert False
    except acom_data.InvalidInput:
        pass
 
    u.add('timmy',dict(password='timmy1'))

    assert u.login('timmy','timmy1')
    assert not u.login('timmy','timmy2')

    timmy = u.lookup('timmy')
    assert 'password' not in timmy
    time1 = timmy['created_date']

    all = u.list()
    assert len(all) == 1
    assert all[0]['name'] == 'timmy'
    assert 'password' not in all[0]

    u.edit('timmy', dict(password='timmy2'))

    assert not u.login('timmy','timmy1')
    assert u.login('timmy','timmy2')

    timmy = u.lookup('timmy', internal=True)
    assert timmy['password'] == 'timmy2'
    time2 = timmy['created_date']
    time3 = timmy['modified_date']
    assert time1 == time2
    assert time3 != time1

    u.delete('timmy')
    assert len(u.list()) == 0
    
    u.add('timmy',dict(password='timmy1'))
    print "ok"

