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
        except acom_data.DoesNotExist:
            flask.abort(404)
    return decorated

@app.route('/')
def hello_world():
    return 'This is Ansible Commander'

@app.route('/api/users/', methods=['GET'])
@requires_auth
@returns_json
def list_users():
    return Users().list()

@app.route('/api/users/', methods=['POST'])
@requires_auth
@returns_json
def add_user():
    return Users().add(jdata())

@app.route('/api/users/<name>/', methods=['GET'])
@requires_auth
@returns_json
def get_user(name):
    return Users().lookup(name)

@app.route('/api/users/<name>/', methods=['PUT'])
@requires_auth
@returns_json
def edit_user(name):
    return Users().edit(name, jdata())

@app.route('/api/users/<name>/', methods=['DELETE'])
@requires_auth
@returns_json
def delete_user(name):
    return Users().delete(name)

@app.route('/api/groups/', methods=['GET'])
@requires_auth
@returns_json
def list_groups():
    return 'success'

@app.route('/api/groups/', methods=['POST'])
@requires_auth
@returns_json
def add_group():
    return 'foo'

@app.route('/api/groups/<name>/', methods=['GET'])
@requires_auth
@returns_json
def get_group(name):
    return 'foo'

@app.route('/api/groups/<name>/', methods=['PUT'])
@requires_auth
@returns_json
def edit_group(name):
    return 'foo'

@app.route('/api/groups/<name>/', methods=['DELETE'])
@requires_auth
@returns_json
def delete_group(name):
    return 'foo'

@app.route('/api/hosts/', methods=['GET'])
@requires_auth
@returns_json
def list_groups():
    return 'foo'

@app.route('/api/hosts/', methods=['POST'])
@requires_auth
@returns_json
def list_groups():
    return 'foo'

@app.route('/api/hosts/<name>', methods=['GET'])
@requires_auth
@returns_json
def list_groups():
    return 'foo'

@app.route('/api/hosts/<name>', methods=['PUT'])
@requires_auth
@returns_json
def list_groups():
    return 'foo'

@app.route('/api/hosts/<name>', methods=['DELETE'])
@requires_auth
@returns_json
def list_groups():
    return 'foo'

@app.route('/api/inventory/hosts/<name>', methods=['GET'])
@requires_auth
@returns_json
def list_groups():
    return 'foo'

if __name__ == '__main__':
    app.debug = DEBUG
    app.run(debug=DEBUG)
