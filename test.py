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
import acom.types.inventory as inventory
import json
import base64

app = commander.app
app.debug = True

acom_data.test_mode()

client = app.test_client()

u = users.Users()
u.clear_test_data()
h = inventory.Hosts()
g = inventory.Groups()
hl = inventory.HostLinks()
gl = inventory.GroupLinks()
h.clear_test_data()
g.clear_test_data()
hl.clear_test_data()
gl.clear_test_data()

app.TEST_MODE=True

def do(method, url, data=None, code=200, username=DEFAULT_USER, password=DEFAULT_PASS):

    method=getattr(client, method)

    if data:
        input = json.dumps(data)
    else:
        input = None

    headers = dict(Authorization="Basic %s" % (base64.b64encode("%s:%s" % (username, password))))
    resp = method(url, data=input, headers=headers)

    data = '\n'.join([ x for x in resp.response])

    if resp.status_code >= 200 and resp.status_code < 300:
        data = json.loads(data)

    if code is not None:
        if resp.status_code != code:
            print "url: %s" % url
            print "got: %s, expected: %s" % (resp.status_code, code)
            assert resp.status_code == code

    return data

def test_index():

    res = do('get', '/api/', code=200)
    assert 'rest_resources' in res
    assert 'version' in res

def test_inventory():

    # show hosts is empty
    res = do('get', '/api/hosts/')
    assert len(res) == 0
    
    # show groups is empty
    res = do('get', '/api/groups/')
    assert len(res) == 0

    # loose hosts
    res = do('post', '/api/hosts/', dict(name='127.0.0.1', vars=dict(c=1000)))
    assert res['name'] == '127.0.0.1'
    res = do('post', '/api/hosts/', dict(name='127.0.0.2', vars=dict(c=1001)))
    res = do('post', '/api/hosts/', dict(name='127.0.0.3', vars=dict(c=1002)))
    res = do('get', '/api/hosts/')
    assert len(res) == 3

    # add some groups
    res = do('post', '/api/groups/', dict(name='alpha', vars=dict(a=1, b=2, c=3)))
    assert res['name'] == 'alpha'
    res = do('post', '/api/groups/', dict(name='beta', vars=dict(a=4, b=5, c=6)))
    res = do('post', '/api/groups/', dict(name='gamma', vars=dict(a=7, b=8, c=9)))
    res = do('get', '/api/groups/')
    assert len(res) == 3

    # edit a host
    res = do('put', '/api/hosts/127.0.0.1', dict(vars=dict(d=9999)))
    res = do('get', '/api/hosts/127.0.0.1')
    assert res['name'] == '127.0.0.1'
    res = do('get', '/api/hosts/')

    # add a host to a group
    res = do('put', '/api/hosts/127.0.0.1', dict(groups=['alpha','beta'], vars=dict(d=99999)))
    res = do('get', '/api/groups/alpha')
    assert '127.0.0.1' in res['_direct_hosts']

    # rename a group and add a group to a subgroup
    res = do('put', '/api/groups/alpha', dict(parents=['gamma']))
    res = do('get', '/api/hosts/127.0.0.1')
    assert res['_blended_vars']['d'] == 99999
    assert res['_blended_vars']['c'] == 3
    # FYI -- host isn't directly in gamma, and doesn't record this fact, though the group knows this
    assert 'alpha' in res['groups'] 
    assert 'beta' in res['groups'] 
    res = do('get', '/api/groups/alpha')
    assert '127.0.0.1' in res['_direct_hosts']
    assert '127.0.0.1' in res['_indirect_hosts']
    res = do('get', '/api/groups/gamma')
    assert '127.0.0.1' not in res['_direct_hosts']
    assert '127.0.0.1' in res['_indirect_hosts']

    # delete a group and make sure the host is edited and does not show it anymore
    res = do('delete', '/api/groups/beta')
    res = do('get', '/api/groups/beta', code=404)
    res = do('get', '/api/hosts/127.0.0.1')
    assert 'beta' not in res['groups']

    res = do('get', '/api/inventory/index')
    assert 'alpha' in res
    assert 'gamma' in res
    assert type(res['alpha']) == list
    assert res['alpha'][0] == '127.0.0.1' 
    
    res = do('get', '/api/inventory/hosts/127.0.0.1', code=200)
    assert type(res) == dict
    assert res['d'] == 99999
    assert res['c'] == 3
    
    # add a second host and delete the first, does the group look right?
    res = do('post', '/api/hosts/', dict(name='foosball.example.com', groups=['alpha', 'gamma']))
    res = do('delete', '/api/hosts/127.0.0.1')
    res = do('get', '/api/groups/alpha')

    assert 'foosball.example.com' in res['_indirect_hosts']
    assert 'foosball.example.com' in res['_direct_hosts']
    assert len(res['_indirect_hosts']) == 1
    assert len(res['_direct_hosts']) == 1
    assert len(res['_ancestors']) == 1
    assert 'gamma' in res['_ancestors']


def test_users():
   
    # test with invalid auth
    res = do('get',  '/api/users/', username='wrong', password='wrong', code=401)

    # list users
    res = do('get',  '/api/users/')
    assert len(res) == 1
    assert res[0]['name'] == 'admin'   

    # add a user
    res = do('post', '/api/users/', data=dict(name='spork',_password='foon'))
    assert res['name'] == 'spork'
    res = do('get',  '/api/users/')
    assert len(res) == 2
    res = do('get',  '/api/users/spork', code=200)
    assert res['name'] == 'spork'

    # edit a user
    res = do('put', '/api/users/spork', dict(comment='narf'))
    res = do('get',  '/api/users/spork', code=200)
    assert res['comment'] == 'narf'
    res = do('get', '/api/users/')
    assert len(res) == 2

    # delete a user
    res = do('delete', '/api/users/spork')
    res = do('get', '/api/users/')
    assert len(res) == 1

