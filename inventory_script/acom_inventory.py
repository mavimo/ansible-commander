#!/usr/bin/env python

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
