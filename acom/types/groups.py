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

class Groups(Base):

   def __init__(self):

       self.TYPE = 'group'
       self.FIELDS = dict(
           primary  = 'name',
           required = [ 'parent' ],
           optional = {},
           protected = [
               'cached_direct_child_groups',
               'cached_direct_child_hosts',
               'cached_all_child_groups',
               'cached_all_child_hosts'
           ],
           private = [],
           hidden  = []
       )
       super(Groups, self).__init__()

    def compute_derived_fields_on_add(self, name, properties):
        properties['created_date'] = time.time()
        self.edit(name, properties, internal=True, hook=True)

    def compute_derived_fields_on_edit(self, name, properties):
        properties['modified_date'] = time.time()
        self.edit(name, properties, internal=True, hook=True)


if __name__ == '__main__':

    acom_data.TESTMODE=True
 
