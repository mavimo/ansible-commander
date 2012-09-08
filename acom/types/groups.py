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

class GroupLinks(acom_data.Base):

    def __init__(self):

        self.TYPE = 'group_link'
        self.FIELDS = dict(
            primary  = 'name',
            required = [ 'parent', 'child'], 
            optional = dict(),
            protected = [
               'created_date',
               'modified_date',
               'parent_id', 
               'child_id'
            ],
            private = [],
            hidden  = []
        )
        super(GroupLinks, self).__init__()

    def check_required_fields(self, fields, edit=False, internal=False):
        super(GroupLinks, self).check_required_fields(fields, edit=edit, internal=internal)
        g = Groups()
        try:
            parent = g.lookup(fields['parent'])
        except acom_data.DoesNotExist:
            raise Exception("parent not found: %s" % fields['parent'])
        try:
            child  = g.lookup(fields['child'])
        except acom_data.DoesNotExist:
            raise Exception("child not found: %s" % fields['child'])

        # force saving links as IDs in case we were originally given names
        fields['parent_id']  = parent['id']
        fields['child_id']   = child['id']
           

class Groups(acom_data.Base):

    def __init__(self):

        self.TYPE = 'group'
        self.FIELDS = dict(
            primary  = 'name',
            required = [],
            optional = dict(description='', comment=''),
            protected = [
                'created_date', 
                'modified_date',
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

    def get_parent_links(self, name):
        info = self.lookup(name)
        gl = GroupLinks()
        parent_links = gl.find('child_id', info['id'])
        return parent_links

    def get_parents(self, name):
        parent_links = self.get_parent_links(name)
        parent_ids = [ p['parent_id'] for p in parent_links ]
        parents = [ self.get_by_id(id) for id in parent_ids ]
        return parents

    def get_ancestors(self, name):
        all = []
        parents = self.get_parents(name)
        all.extend(parents)
        for p in parents:
            all.extend(self.get_ancestors(p['name']))
        return all

    def get_child_links(self, name):
        info = self.lookup(name)
        gl = GroupLinks()
        child_links = gl.find('parent_id', info['id'])
        return child_links
    
    def get_children(self, name):
        child_links = self.get_child_links(name)
        child_ids = [ p['child_id'] for p in child_links ]
        children = [ self.get_by_id(id) for id in child_ids ]
        return children

    def set_parents(self, name, parent_names):

        gl = GroupLinks()
        info = self.lookup(name)

        my_thing_id = info['id']
        existing_parents = self.get_parents(name)
        existing_parent_ids = [ x['id'] for x in existing_parents ]
 
        for parent_name in parent_names:
            parent          = self.lookup(parent_name)
            parent_thing_id = parent['id']
            parent_name     = parent['name']

            if parent_thing_id in existing_parent_ids:
                pass
            else: 
                link_name= "%s-%s" % (parent_thing_id, my_thing_id)
                gl.add(link_name, dict(child=name, parent=parent_name))

        # delete parents that we have disowned! (Found A Better Family?)
        for parent_thing_id in existing_parent_ids:
            if parent_thing_id not in parent_ids:
                link_name = "%s-%s" % (parent_thing_id, my_thing_id)
                gl.delete(link_name) 

        return self.get_parents(name)

if __name__ == '__main__':

    acom_data.test_mode()

    print 'adding united states'
    g = Groups()
    gl = GroupLinks()
    g.clear_test_data()
    gl.clear_test_data()

    g1 = g.add('united_states', dict())
    assert g1['name'] == 'united_states'

    print 'adding north carolina'
    g2 = g.add('north_carolina', dict())
    assert g2['name'] == 'north_carolina'

    print 'adding south carolina'
    g3 = g.add('south_carolina', dict())
    assert g3['name'] == 'south_carolina'
 
    print 'north_carolina is in the united_states'
    link = g.set_parents('north_carolina', [ 'united_states'])

    print 'south_carolina is in the united_states'
    link2 = g.set_parents('south_carolina', [ 'united_states'])

    print 'both north_carolina and south_carolina are sub groups of the united states'
    children = g.get_children('united_states')
    assert len(children) == 2

    print 'north carolina has no subgroups'
    children = g.get_children('north_carolina')
    print children
    assert len(children) == 0

    print 'the united_states has no parent groups'
    parents = g.get_parents('united_states')
    print parents
    assert len(parents) == 0

    print 'the united_states is a parent group of north_carolina'
    parents = g.get_parents('north_carolina')
    assert len(parents) == 1

    print 'adding raleigh'
    g4 = g.add('raleigh', dict())
    
    print 'raleigh is in north_carolina'
    g.set_parents('raleigh', ['north_carolina'])

    print 'raleigh has in-order ancestors'
    ancestors = g.get_ancestors('raleigh')
    assert len(ancestors) == 2

    print "ok"

