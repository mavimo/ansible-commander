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

import time
import acom.data as acom_data

class Junk(acom_data.Base):
   
    def __init__(self):
    
        self.TYPE = 'junk'
        self.FIELDS = dict(
            primary    = 'name',
            required   = [ 'info' ],
            optional   = dict(labs=''),
            protected  = [ 'created_date', 'modified_date' ], 
            private    = [],
            hidden     = []
        )
        super(Junk, self).__init__()

    def compute_derived_fields_on_add(self, name, properties):
        properties['created_date'] = time.time()
        self.edit(name, properties, internal=True, hook=True)

    def compute_derived_fields_on_edit(self, name, properties):
        properties['modified_date'] = time.time()
        self.edit(name, properties, internal=True, hook=True)


if __name__ == '__main__':

    acom_data.TESTMODE=True

    j = Junk()
    j.clear_testmode()

    print 'insert pinky'
    print j.add('pinky', dict(info='narf'))

    try:
        print 'insert pinky'
        print j.add('pinky', dict(info='narf'))
    except AlreadyExists:
        print 'already exists'

    print 'insert brain'
    print j.add('brain', dict(info='aypwip'))

    print 'list'
    print j.list()

    print 'lookup pinky'
    print j.lookup('pinky')

    print 'edit pinky'
    j.edit('pinky', dict(info='troz', labs='acme'))

    # again
    j.edit('pinky', dict(info='fjord', labs='acme'))

    # with invalid fields
    try:
        j.edit('pinky', dict(info='fjord', labs='acme', imaginary='...'))
    except InvalidInput:
        print 'invalid input blocked'
        pass

    # with attempting to rename to brain
    try:
        j.edit('pinky', dict(name='brain'))
    except AlreadyExists:
        print 'rename blocked'
        pass

    # with attempting to rename to Pinkasso
    j.edit('pinky', dict(name='pinkasso', info='le narf'))

    print 'lookup pinky'
    print j.lookup('pinkasso')

    print 'lookup brain'
    print j.find('name','brain')

    print 'lookup snowball'
    print j.find('name','snowball')

    print 'delete brain'
    print j.delete('brain')

    print 'list'
    print j.list()
 

