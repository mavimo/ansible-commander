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

VERSION = '0.1'

DEBUG=True
DEFAULT_USER='admin'
DEFAULT_PASS='gateisdown'


import flask
from flask import request
import json
import random
from functools import wraps
from acom import data as acom_data
from acom.types.users import Users
from acom.types.inventory import Hosts, Groups


app = flask.Flask(__name__)
random.seed()

def jdata():
    try:
        return json.loads(request.data)
    except ValueError:
        raise Exception("failed to parse JSON: %s" % request.data)

def check_auth(username, password):
    u = Users()
    all = u.list(internal=True)
    if len(all) == 0 and (username == DEFAULT_USER and password == DEFAULT_PASS):
        u.add(dict(name=DEFAULT_USER, _password=DEFAULT_PASS))
        return True
    return u.login(username, password)

def authenticate(msg='Authenticate'):
    message = dict(message=msg)
    resp = flask.jsonify(message)
    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Ansible Commander"'
    return resp

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = flask.request.authorization
        if not auth: 
            return authenticate()
        elif not check_auth(auth.username, auth.password):
            return authenticate("Authentication Failed.")
        return f(*args, **kwargs)
    return decorated

def returns_json(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            return json.dumps(result)
        except acom_data.DoesNotExist, e:
            flask.abort(404)
    return decorated

@app.route('/api/', methods=['GET'])
@returns_json
def hello_world():
    return dict(
        rest_resources = dict(
            users  = dict(href='/api/users/', fields=Users().FIELDS),
            hosts  = dict(href='/api/hosts/', fields=Hosts().FIELDS),
            groups = dict(href='/api/groups/', fields=Groups().FIELDS),
        ),
        version=VERSION,
    )


@app.route('/api/users/<name>', methods=['GET','PUT','DELETE'])
@requires_auth
@returns_json
def user_service(name):
    if request.method == 'GET':
        return Users().lookup(name)
    elif request.method == 'PUT':
        return Users().edit(name, jdata())
    elif request.method == 'DELETE':
        return Users().delete(name)

@app.route('/api/users/', methods=['GET', 'POST'])
@requires_auth
@returns_json
def users_service():
    if request.method == 'GET':
        return Users().list()
    elif request.method == 'POST':
        return Users().add(jdata())

@app.route('/api/groups/', methods=['GET','POST'])
@requires_auth
@returns_json
def groups_service():
    if request.method == 'GET':
        return Groups().list()
    elif request.method == 'POST':
        return Groups().add(jdata())

@app.route('/api/groups/<name>', methods=['GET','PUT','DELETE'])
@requires_auth
@returns_json
def get_group(name):
    if request.method == 'GET':
        return Groups().lookup(name)
    elif request.method == 'PUT':
        return Groups().edit(name, jdata())
    elif request.method == 'DELETE':
        return Groups().delete(name)

@app.route('/api/hosts/', methods=['GET','POST'])
@requires_auth
@returns_json
def list_hosts():
    if request.method == 'GET':
        return Hosts().list()
    elif request.method == 'POST':
        return Hosts().add(jdata())

@app.route('/api/hosts/<name>', methods=['GET','PUT','DELETE'])
@requires_auth
@returns_json
def get_host(name):
    if request.method == 'GET':
        return Hosts().lookup(name)
    elif request.method == 'PUT':
        return Hosts().edit(name, jdata())
    elif request.method == 'DELETE':
        return Hosts().delete(name)

@app.route('/api/inventory/hosts/<name>', methods=['GET'])
@returns_json
def inventory_host_info(name):
    return Hosts().lookup(name)['_blended_vars']

@app.route('/api/inventory/index', methods=['GET'])
@returns_json
def inventory_index():
    groups = Groups().list()
    results = {}
    for g in groups:
        results[g['name']] = g['_indirect_hosts']
    return results

if __name__ == '__main__':
    app.debug = DEBUG
    app.run(debug=DEBUG)
