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
from functools import wraps
from acom import data
from acom.types.users import Users

app = flask.Flask(__name__)

def check_auth(username, password):
    u = Users()
    all = u.list()
    if len(all) == 0 and (username == DEFAULT_USER and password == DEFAULT_PASS):
        u.add(DEFAULT_USER, dict(password=DEFAULT_PASS))
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

@app.route('/')
def hello_world():
    return 'This is Ansible Commander'

@app.route('/api/groups')
@requires_auth
def groups():
    return 'success'

if __name__ == '__main__':
    app.run(debug=DEBUG)
