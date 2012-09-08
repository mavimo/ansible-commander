import psycopg2
import ConfigParser
import psycopg2.extras as extras
import json

# TODO: make a seperate config class
parser  = ConfigParser.ConfigParser()
parser.read("/etc/ansible/commander.cfg")

dbname  = 'ansible_commander'
dbuser  = 'ansible_commander'
dbpass  = parser.get('database', 'password')
connstr = "dbname='%s' user='%s' host='localhost' password='%s'" % (dbname,dbuser,dbpass)

conn = psycopg2.connect(connstr)

class DataException(Exception):
   pass

class AlreadyExists(DataException):
   pass

class InvalidInput(DataException):
   pass

class DoesNotExist(DataException):
   pass

class Ambigious(DataException):
   pass

class Base(object):

    def __init__(self):
        self.type = None

    def cursor(self):
        return conn.cursor()

    def check_required_fields(self, fields, edit=False):
 
        if not edit:
            if fields.get(self.FIELDS['primary'], None) is None:
                raise InvalidInput("missing primary field: %s" % self.FIELDS['primary'])
     
            # all required fields are set
            for f in self.FIELDS['required']:
                if f not in fields:
                    raise InvalidInput("field %s if required" % f)

            # any optional fields get set to defaults if missing
            for f in self.FIELDS['optional']:
                if f not in fields:
                    fields[f] = self.FIELDS['optional'][f] 

        # no unexpected fields
        for f in fields:
            if f not in self.FIELDS['required'] and f not in self.FIELDS['optional'] and f != self.FIELDS['primary']:
                raise InvalidInput("invalid field %s" % f)

    def add(self, properties):
        self.check_required_fields(properties)
        primary = self.FIELDS['primary']
        matches = self.lookup(properties[primary])
        if len(matches) != 0:
            raise AlreadyExists()
        return self._insert(properties)

    def edit(self, name, properties):
        primary = self.FIELDS['primary']
        self.check_required_fields(properties, edit=True)
        if primary in properties:
            matches = self.lookup(properties[primary])
            if len(matches):
                raise AlreadyExists()
        matches = self.lookup(name)
        if len(matches) == 0:
            raise DoesNotExist()
        elif len(matches) != 1:
            raise Ambigious()
        id = matches[0]['id']

        for (k,v) in properties.iteritems():
            if k not in matches[0]:
                # TODO: would be nice to execute many here
                self._insert_kv(id,k,v)
            elif matches[0][k] != properties[k]:
                self._update_kv(id,k,v)

    def _insert_kv(self, id, k, v):
        cur = self.cursor()
        v=json.dumps(v)
        sth = """
           INSERT INTO properties (thing_id, key, value)
           VALUES (%s,%s,%s)
        """
        cur.execute(sth, [id,k,v])
        conn.commit()

    def _update_kv(self, id, k, v):
        cur = self.cursor()
        v=json.dumps(v)
        sth = """
            UPDATE properties 
            SET 
               value=%s
            WHERE
               id IN (
                    SELECT id FROM properties
                    WHERE thing_id=%s
                    AND key=%s
               )
        """
        cur.execute(sth,[v,id,k])
        conn.commit()
 
    def _insert(self, properties):
        primary = self.FIELDS['primary']
        cur = self.cursor()
        sth = """
            INSERT INTO thing (type) VALUES (%s)
            RETURNING id
        """
        cur.execute(sth, [self.TYPE])
        tid = cur.fetchone()[0]

        inserts = []
        for (k,v) in properties.iteritems():
            inserts.append((tid, k, json.dumps(v))) 
       
        sth = """
            INSERT INTO properties (thing_id,key,value) VALUES(%s,%s,%s)
        """
        cur.executemany(sth, inserts)
        conn.commit()
        matches = self.find(primary, properties[primary])
        return matches[0]

    def list(self):
        cur = self.cursor()
        sth = """
             SELECT t.id, p.id, p.key, p.value 
             FROM thing t
             LEFT JOIN properties p
             ON p.thing_id = t.id
             WHERE type    = %s

        """

        cur.execute(sth, [self.TYPE])
        db_results = cur.fetchall()
        return self._reformat(db_results)

    def _reformat(self, db_results):

        results = {}
        for (tid, pid, key, value) in db_results:
            if not tid in results:
                results[tid] = {}
            results[tid][key] = json.loads(value) 
            results[tid]['id'] = tid
        return results.values()
        
    def find(self, key, value):
        cur = self.cursor()
        # all values are stored in JSON in the DB, so ookups must also jsonify first
        value = json.dumps(value)
        sth = """
             SELECT t.id, p.id, p.key, p.value 
             FROM thing t, properties p
             WHERE p.thing_id = t.id
             AND t.id IN (
                 SELECT t.id
                 FROM thing t
                 LEFT JOIN properties p
                 ON p.thing_id = t.id
                 WHERE type  = %s
                 AND p.key   = %s
                 AND p.value = %s
             )
        """
        cur.execute(sth, [self.TYPE,key,value])
        db_results = cur.fetchall()
        matches = self._reformat(db_results)
        return matches
  
    def lookup(self, value):
        return self.find(self.FIELDS['primary'], value)    

    def delete(self, value):
        cur = self.cursor()
        obj = self.find(self.FIELDS['primary'], value)    
        if len(obj) == 0:
            pass
        elif len(obj) != 1:
            raise Ambigious()
        id = obj[0]['id']
        sth = """
           DELETE FROM thing where id=%s
        """
        cur.execute(sth, [id])
        conn.commit()

    def clear(self):
        cur = self.cursor()
        sth = """
            DELETE from thing where type=%s
        """
        cur.execute(sth, [self.TYPE])
        conn.commit()
            

class Groups(Base):

   def __init__(self):

       self.TYPE = 'group'
       self.FIELDS = dict(
           primary  = 'name',
           required = [ 'parent' ],
           optional = {},
           private = [
               'cached_direct_child_groups',
               'cached_direct_child_hosts',
               'cached_all_child_groups',
               'cached_all_child_hosts'
           ]
       )

class Junk(Base):
   
    def __init__(self):
    
        self.TYPE = 'group'
        self.FIELDS = dict(
            primary  = 'name',
            required = [ 'info' ],
            optional = dict(labs=''),
            private = []
        )


if __name__ == '__main__':

    j = Junk()
    j.clear()

    print 'insert pinky'
    print j.add(dict(name='pinky', info='narf'))

    try:
        print 'insert pinky'
        print j.add(dict(name='pinky', info='narf'))
    except AlreadyExists:
        print 'already exists'

    print 'insert brain'
    print j.add(dict(name='brain', info='aypwip'))

    print 'list'
    print j.list()

    print 'lookup pinky'
    print j.lookup('pinky')

    print 'edit pinky'
    j.edit('pinky', dict(info='troz', labs='acme'))

    # again
    j.edit('pinky', dict(info='fjord', labs='acme'))

    # with invalid fields
    try:
        j.edit('pinky', dict(info='fjord', labs='acme', imaginary='...'))
    except InvalidInput:
        print 'invalid input blocked'
        pass

    # with attempting to rename to brain
    try:
        j.edit('pinky', dict(name='brain'))
    except AlreadyExists:
        print 'rename blocked'
        pass

    # with attempting to rename to Pinkasso
    j.edit('pinky', dict(name='pinkasso', info='le narf'))

    print 'lookup pinky'
    print j.lookup('pinkasso')

    print 'lookup brain'
    print j.find('name','brain')

    print 'lookup snowball'
    print j.find('name','snowball')

    print 'delete brain'
    print j.delete('brain')

    print 'list'
    print j.list()
 

