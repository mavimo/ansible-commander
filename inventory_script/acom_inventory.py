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

import httplib
import ConfigParser
import sys

parser = ConfigParser.ConfigParser()
parser.read("acom_inventory.cfg")

# inventory secret is used to prevent just-any host from reading hostnames and variable info
# it is NOT usable to log in to the REST API and do anything else

secret = parser.get('inventory','secret')
server = parser.get('inventory','server')
api_prefix = parser.get('inventory','api_prefix')

if len(sys.argv) == 2 and (sys.argv[1] == '--list'):
    h = httplib.HTTPConnection(server)
    h.request('POST', "%s/inventory/index" % (api_prefix), secret, {})
    r = h.getresponse()
    print r.read()
elif len(sys.argv) == 3 and (sys.argv[1] == '--host'): 
    h = httplib.HTTPConnection(server)
    h.request('POST', "%s/inventory/hosts/%s" % (api_prefix, sys.argv[2]), secret, {})
    r = h.getresponse()
    print r.read()
