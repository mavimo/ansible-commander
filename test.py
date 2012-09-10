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

# FIXME: this currently does NOT run against the test database

DEFAULT_USER='admin'
DEFAULT_PASS='gateisdown'

import commander
import acom.data as acom_data
import acom.types.users as users
import json
import base64

app = commander.app
app.debug = True

acom_data.test_mode()

client = app.test_client()

u = users.Users()
u.clear_test_data()

app.TEST_MODE=True

def do(method, url, data=None, code=None, username=DEFAULT_USER, password=DEFAULT_PASS):
    print "url=%s" % url
    print "method=%s" % method
    method=getattr(client, method)

    if data:
        input = json.dumps(data)
        print "input=%" % input
    else:
        input = None

    headers = dict(Authorization="Basic %s" % (base64.b64encode("%s:%s" % (username, password))))
    resp = method(url, data=data, headers=headers)

    print "code=%s" % resp.status_code

    data = '\n'.join([ x for x in resp.response])

    print "data=%s" % data
    data = json.loads(data)

    if code is not None:
        assert resp.status_code == code

    return data

def test_users():

    res = do('get', '/api/users/', code=200)
    print res

    res = do('get', '/api/users/', code=200)
    print res    
    raise Exception("stop") 
