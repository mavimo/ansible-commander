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


class HostLinks(acom_data.Base):

    def __init__(self):

        self.TYPE = 'host_link'
        self.FIELDS = dict(
            primary  = 'name',
            required = [ 'host', 'group'],
            optional = dict(),
            protected = [ '_created_date', '_modified_date', '_host_id', '_group_id' ],
            private = [],
            hidden  = []
        )
        super(HostLinks, self).__init__()

    def check_required_fields(self, fields, edit=False, internal=False):
        super(HostLinks, self).check_required_fields(fields, edit=edit, internal=internal)
        g = Groups()
        h = Hosts()
        try:
            group = g.lookup(fields['group'])
        except acom_data.DoesNotExist:
            raise Exception("group not found: %s" % fields['group'])
        try:
            host  = h.lookup(fields['host'])
        except acom_data.DoesNotExist:
            raise Exception("host not found: %s" % fields['host'])

        # force saving links as IDs in case we were originally given names
        fields['_host_id']    = host['id']
        fields['_group_id']   = group['id']


class GroupLinks(acom_data.Base):

    def __init__(self):

        self.TYPE = 'group_link'
        self.FIELDS = dict(
            primary  = 'name',
            required = [ 'parent', 'child'], 
            optional = dict(),
            protected = [ '_created_date', '_modified_date', '_parent_id', '_child_id' ],
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
        fields['_parent_id']  = parent['id']
        fields['_child_id']   = child['id']

class Hosts(acom_data.Base):

    def __init__(self):

        self.TYPE = 'host'
        self.FIELDS = dict(
            primary  = 'name',
            required = [],
            optional = dict(vars={}, description='', comment=''),
            protected = [ '_created_date', '_modified_date', '_groups', '_blended_vars' ],
            private = [],
            hidden  = []
        )
        super(Hosts, self).__init__()
           
    def compute_derived_fields_on_add(self, name, properties):
        properties['_created_date'] = time.time()
        self.edit(name, properties, internal=True, hook=True)
        self.compute_blended_vars(name)

    def compute_derived_fields_on_edit(self, name, properties):
        properties['_modified_date'] = time.time()
        self.edit(name, properties, internal=True, hook=True)
        self.compute_blended_vars(name)

    def compute_blended_vars(self, name):
        g = Groups()
        info = self.lookup(name)

        vars = {}
        if '_groups' in info:
            chain = []
            for gname in info['_groups']:
                chain.append(g.lookup(gname))
                ancestors = g.get_ancestors(gname)
                chain.extend(ancestors)
            chain.reverse()
            for group_info in chain:
                vars.update(group_info['vars'])
            vars.update(info['vars'])

        else:
            vars = info['vars']        

        self.edit(name, dict(_blended_vars=vars), internal=True, hook=True)

    def set_groups(self, name, group_names):

        assert type(group_names) == list

        hl = HostLinks()
        g  = Groups()
        info = self.lookup(name)

        my_thing_id = info['id']
        existing_groups = self.get_groups(name)
        existing_group_ids = [ x['id'] for x in existing_groups ]

        group_ids =  []
        for group_name in group_names:
            group           = g.lookup(group_name)
            group_thing_id  = group['id']
            group_ids.append(group_thing_id)
            group_name      = group['name']

            if group_thing_id in existing_group_ids:
                pass
            else:
                link_name= "%s-%s" % (group_thing_id, my_thing_id)
                hl.add(link_name, dict(host=name, group=group_name))

        for group_thing_id in existing_group_ids:
            if group_thing_id not in group_ids:
                link_name = "%s-%s" % (group_thing_id, my_thing_id)
                ginfo = g.get_by_id(group_thing_id)
                g.recompute_relationships(ginfo['name'])
                gl.delete(link_name)

        for gname in group_names:
            g.recompute_relationships(gname)

        self.edit(name, dict(_groups=group_names), internal=True, hook=True)
        self.compute_blended_vars(name)
        return self.get_groups(name)

    def get_host_links(self, name):
        info = self.lookup(name)
        gl = HostLinks()
        host_links = gl.find('_host_id', info['id'])
        return host_links

    def get_groups(self, name):
        g = Groups()
        host_links = self.get_host_links(name)
        group_ids = [ p['_group_id'] for p in host_links ]
        groups = [ g.get_by_id(id) for id in group_ids ]
        return parents

    def hosts_for_group_name(self, group_name):
        g = Groups()
        info = g.lookup(group_name)
        gl = HostLinks()
        host_links = gl.find('_group_id', info['id'])
        host_ids = [ p['_host_id'] for p in host_links ]
        hosts = [ self.get_by_id(id) for id in host_ids ]
        return hosts

class Groups(acom_data.Base):

    def __init__(self):

        self.TYPE = 'group'
        self.FIELDS = dict(
            primary  = 'name',
            required = [],
            optional = dict(vars={}, description='', comment=''),
            protected = [ 
                '_created_date', '_modified_date', 
                '_ancestors', '_descendents', '_parents', '_children', 
                '_indirect_hosts', '_direct_hosts'
            ],
            private = [],
            hidden  = []
        )
        super(Groups, self).__init__()

    def compute_derived_fields_on_add(self, name, properties):
        properties['_created_date'] = time.time()
        self.edit(name, properties, internal=True, hook=True)
        self.recompute_relationships(name)
        
    def compute_derived_fields_on_edit(self, name, properties):
        properties['_modified_date'] = time.time()
        self.edit(name, properties, internal=True, hook=True)
        self.recompute_relationships(name)

    def get_parent_links(self, name):
        info = self.lookup(name)
        gl = GroupLinks()
        parent_links = gl.find('_child_id', info['id'])
        return parent_links

    def get_parents(self, name):
        parent_links = self.get_parent_links(name)
        parent_ids = [ p['_parent_id'] for p in parent_links ]
        parents = [ self.get_by_id(id) for id in parent_ids ]
        return parents

    def get_ancestors(self, name):
        all = []
        parents = self.get_parents(name)
        all.extend(parents)
        for p in parents:
            all.extend(self.get_ancestors(p['name']))
        return all

    def get_descendents(self, name):
        all = []
        children = self.get_children(name)
        all.extend(children)
        for p in children:
            all.extend(self.get_descendents(p['name']))
        return all

    def get_child_links(self, name):
        info = self.lookup(name)
        gl = GroupLinks()
        child_links = gl.find('_parent_id', info['id'])
        return child_links
    
    def get_children(self, name):
        child_links = self.get_child_links(name)
        child_ids = [ p['_child_id'] for p in child_links ]
        children = [ self.get_by_id(id) for id in child_ids ]
        return children

    def set_parents(self, name, parent_names):

        assert type(parent_names) == list

        gl = GroupLinks()
        info = self.lookup(name)

        my_thing_id = info['id']
        existing_parents = self.get_parents(name)
        existing_parent_ids = [ x['id'] for x in existing_parents ]

        parent_ids = [] 
        for parent_name in parent_names:
            parent          = self.lookup(parent_name)
            parent_thing_id = parent['id']
            parent_ids.append(parent_thing_id)
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


        # keep track of static data (optimized for retrieval, not so much for entry)
        ancestors = self.get_ancestors(name)
        descendents = self.get_descendents(name)
        for d in descendents:
            self.recompute_relationships(d['name'])
        self.recompute_relationships(name)
        for a in ancestors:
            self.recompute_relationships(a['name'])

        return self.get_parents(name)


    def recompute_relationships(self, name):

        info = self.lookup(name)
        ancestors = self.get_ancestors(name)
        descendents = self.get_descendents(name)
        direct_parents = self.get_parents(name)
        direct_children = self.get_children(name)

        # recompute derived relationships
        properties = {}
        properties['_ancestors']   = list(set([ p['name'] for p in ancestors ]))
        properties['_descendents'] = list(set([ p['name'] for p in descendents ]))
        properties['_parents']     = [ p['name'] for p in direct_parents ]
        properties['_children']    = [ p['name'] for p in direct_children ] 
        
        h = Hosts()
        all_hosts = []
        for d in properties['_descendents']:
            descendent_hosts = h.hosts_for_group_name(d)
            all_hosts.extend(descendent_hosts)
        direct_hosts = h.hosts_for_group_name(name)
        all_hosts.extend(direct_hosts)
        properties['_indirect_hosts'] = list(set([ x['name'] for x in all_hosts ]))
        properties['_direct_hosts']   = list(set([ x['name'] for x in direct_hosts ]))

        self.edit(name, properties, internal=True, hook=True)


if __name__ == '__main__':

    acom_data.test_mode()

    #print 'adding united states'
    g = Groups()
    gl = GroupLinks()
    hl = HostLinks()
    h = Hosts()
    g.clear_test_data()
    gl.clear_test_data()
    h.clear_test_data()
    hl.clear_test_data()

    h.add('uno', dict(vars={}, comment='asdf'))
    h.add('dos', dict(vars={}, comment='jkl;'))
    h.add('tres', dict(vars={}, comment='mnop'))
    h.add('quatro', dict(vars={}, comment='qrst'))

    g1 = g.add('united_states', dict(comment='of america', vars=dict(when=1776, a=2, b=3, c=[4,5,6])))
    assert g1['name'] == 'united_states'

    #print 'adding north carolina'
    g2 = g.add('north_carolina', dict(vars=dict(when=1789, bonus='yes')))
    assert g2['name'] == 'north_carolina'

    #print 'adding south carolina'
    g3 = g.add('south_carolina', dict())
    assert g3['name'] == 'south_carolina'
 
    #print 'north_carolina is in the united_states'
    link = g.set_parents('north_carolina', [ 'united_states'])

    #print 'south_carolina is in the united_states'
    link2 = g.set_parents('south_carolina', [ 'united_states'])

    #print 'both north_carolina and south_carolina are sub groups of the united states'
    children = g.get_children('united_states')
    assert len(children) == 2

    #print 'north carolina has no subgroups'
    children = g.get_children('north_carolina')
    #print children
    assert len(children) == 0

    #print 'the united_states has no parent groups'
    parents = g.get_parents('united_states')
    #print parents
    assert len(parents) == 0

    #print 'the united_states is a parent group of north_carolina'
    parents = g.get_parents('north_carolina')
    assert len(parents) == 1

    #print 'adding raleigh'
    g4 = g.add('raleigh', dict(vars=dict(when=1792, acorn=True)))
    
    #print 'raleigh is in north_carolina'
    g.set_parents('raleigh', ['north_carolina'])

    #print 'raleigh has in-order ancestors'
    ancestors = g.get_ancestors('raleigh')
    assert len(ancestors) == 2

    #print 'united_states has 3 descendents'
    descendents = g.get_descendents('united_states')
    assert len(descendents) == 3

    #print g.lookup('united_states')
    #print g.lookup('raleigh')
    
    
    h.set_groups('uno', [ 'north_carolina', 'south_carolina' ])
    h.set_groups('dos', [ 'raleigh' ])
    h.set_groups('tres', [ 'south_carolina' ])
    h.set_groups('quatro', ['united_states', 'north_carolina'])

    # check redirect and indirect host counts
    nc = g.lookup('north_carolina')
    assert len(nc['_indirect_hosts']) == 3    
    assert len(nc['_direct_hosts']) == 2 
    assert len(nc['_indirect_hosts']) == 3    
    us = g.lookup('united_states')
    assert len(us['_indirect_hosts']) == 4    
    assert len(us['_direct_hosts']) == 0
    
    h.edit('uno', dict(comment='editing uno'))
    dos = h.lookup('dos')
    uno = h.lookup('uno')
    uno_vars = uno['_blended_vars']

    assert uno_vars['when'] == 1789
    assert uno_vars['a'] == 2
    assert uno['comment'] == 'editing uno'

    print 'ok'
